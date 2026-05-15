import random
from datetime import timedelta
from accounts.tasks import send_email_task
from django.utils import timezone
from django.contrib.auth.hashers import make_password , check_password

class OTPService:
    OTP_EXPIRY_MINUTES = 5
    RESEND_COOLDOWN_SECONDS = 60
    MAX_ATTEMPTS = 3

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))
    
    @classmethod
    def create_and_send_otp(cls,user):
        otp = cls.generate_otp()
        user.otp = make_password(otp)
        user.otp_created_at = timezone.now()
        user.otp_attempt = 0
        user.otp_block_time = None
        user.save(update_fields=[
            "otp","otp_created_at","otp_attempt","otp_block_time"
        ])
        subject = "Your Verification Code"
        message = f"""
Hello,

Your verification code is:

{ otp }

This code will expire in 5 minutes.

If you did not request this code, please ignore this email.

Thank you,
Blogs Team
"""
        send_email_task.delay(subject=subject,message=message,recipient_list=[user.email])
        return otp
    
    @classmethod
    def create_and_send_email_otp(cls,user):
        otp = cls.generate_otp()
        user.otp = make_password(otp)
        user.otp_created_at = timezone.now()
        user.otp_attempt = 0
        user.otp_block_time = None
        user.save(update_fields=[
            "otp","otp_created_at","otp_attempt","otp_block_time"
        ])
        subject = "Verify Your New Email Address"
        message = f"""
Hello,

We received a request to change the email address associated with your account.

Use the verification code below to confirm your new email address:

{ otp }
This code will expire in 5 minutes.

If you did not request this change, please ignore this email and secure your account.

Thank you,
Blogs Team
"""
        send_email_task.delay(subject=subject,message=message,recipient_list=[user.pending_email])
        return otp
    
    @classmethod
    def verify_otp(cls,entered_otp,user):
        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=cls.OTP_EXPIRY_MINUTES):
            return False ,"Your OTP has expired. Please request a new one."
        
        if user.otp_block_time and timezone.now() < user.otp_block_time:
            remaining_seconds = int((user.otp_block_time - timezone.now()).total_seconds())
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return False , f"You have reached maximum attempts. Try again in {minutes}m {seconds}s."
        
        if check_password(entered_otp,user.otp):
            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.otp_block_time = None
            user.otp_attempt = 0
            user.save(update_fields=["is_active","otp","otp_created_at","otp_block_time","otp_attempt"])
            return True , "OTP verified successfully."
        
        user.otp_attempt += 1
        if user.otp_attempt >= cls.MAX_ATTEMPTS:
            user.otp_block_time = timezone.now() + timedelta(minutes=1)
            user.otp_attempt = 0
            user.save(update_fields=["otp_attempt", "otp_block_time"])
            return False, "Too many attempts. Try again in 1m 0s"
        remaining_attempts = cls.MAX_ATTEMPTS - user.otp_attempt
        user.save(update_fields=["otp_attempt"])
        return False, f"Invalid OTP. You have {remaining_attempts} attempts left."
    
    @classmethod
    def verify_email_otp(cls,entered_otp,user):
        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=cls.OTP_EXPIRY_MINUTES):
            return False ,"Your OTP has expired. Please request a new one."
        
        if user.otp_block_time and timezone.now() < user.otp_block_time:
            remaining_seconds = int((user.otp_block_time - timezone.now()).total_seconds())
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return False , f"You have reached maximum attempts. Try again in {minutes}m {seconds}s."
        
        if check_password(entered_otp,user.otp):
            user.email = user.pending_email
            user.pending_email = None
            user.otp = None
            user.otp_created_at = None
            user.otp_block_time = None
            user.otp_attempt = 0
            user.save(update_fields=["email","otp","otp_created_at","otp_block_time","otp_attempt"])
            return True , "Email verified successfully."
        
        user.otp_attempt += 1
        if user.otp_attempt >= cls.MAX_ATTEMPTS:
            user.otp_block_time = timezone.now() + timedelta(minutes=1)
            user.otp_attempt = 0
            user.save(update_fields=["otp_attempt", "otp_block_time"])
            return False, "Too many attempts. Try again in 1m 0s"
        remaining_attempts = cls.MAX_ATTEMPTS - user.otp_attempt
        user.save(update_fields=["otp_attempt"])
        return False, f"Invalid OTP. You have {remaining_attempts} attempts left."
    
    @classmethod
    def can_resend_otp(cls, user):
        if user.otp_block_time and timezone.now() < user.otp_block_time:
            remaining = int((user.otp_block_time - timezone.now()).total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60
            return False, f"Try again in {minutes}m and {seconds}s"
        if user.otp_created_at:
            cooldown_end = user.otp_created_at + timezone.timedelta(
                seconds=cls.RESEND_COOLDOWN_SECONDS
            )
            if timezone.now() < cooldown_end:
                remaining = int((cooldown_end - timezone.now()).total_seconds())
                minutes = remaining // 60
                seconds = remaining % 60
                return False, f"Please wait {minutes}m and {seconds}s before resending OTP"
        return True , "New OTP sent successfully"
from django import forms
from .tasks import send_email_task
from .models import CustomUser , Profile
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm , PasswordResetForm , SetPasswordForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email","username","password1","password2"]        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"
        self.fields["username"].widget.attrs["placeholder"] = "Enter Username"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Enter Confirm Password"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user:
            if not user.is_active:
                user.delete()
        return email
    
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class":"form-control","placeholder":"Enter Your Email","autocomplete": "email"})
    )
    password = forms.CharField(
       widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Enter Your Password","autocomplete": "current-password"}) 
    )

class OtpForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Verify OTP"})
    )

class CustomPasswordResetForm(PasswordResetForm):
    def save(self, domain_override = None, subject_template_name = None, email_template_name = None, use_https = False, token_generator = default_token_generator, from_email = None, request = None, html_email_template_name =None, extra_email_context = None):
        email = self.cleaned_data.get("email")
        for user in self.get_users(email):
            context = {
                "email":user.email,
                "domain":request.get_host(),
                "site_name":"Your Website",
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                "user":user,
                "token":token_generator.make_token(user),
                "protocol":"https" if use_https else "http"

            }
            subject = render_to_string(
                subject_template_name,
                context
            ).strip()

            message = render_to_string(
                email_template_name,
                context
            )

            send_email_task.delay(
                subject,
                message,
                [user.email]   
            )

class CustomPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Enter New Password"})
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Confirm New Password"})
    )

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.exclude(id=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""

class EmailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.exclude(id=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
class EmailOtpForm(forms.Form):
    otp = forms.CharField(
        label="OTP",
        max_length=6,
        widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Verify OTP"})
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["name","profile_image"]
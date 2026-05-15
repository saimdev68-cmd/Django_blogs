import logging
from .forms import RegisterForm , LoginForm , OtpForm , CustomPasswordResetForm , CustomPasswordForm , ProfileForm , UserForm , EmailForm , EmailOtpForm
from .models import CustomUser , Profile 
from .services.otp_service import OTPService
from django.views import generic , View
from django.contrib import messages
from django.shortcuts import redirect , get_object_or_404 , render
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth import login , authenticate , logout
from django.contrib.auth.views import PasswordResetView , PasswordResetDoneView ,  PasswordResetConfirmView , PasswordResetCompleteView , PasswordChangeView , PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)

# Create your views here.

class SignUpView(generic.CreateView):
    template_name = "signup.html"
    form_class = RegisterForm

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                OTPService.create_and_send_otp(user)
                self.request.session["signup_user_id"] = user.id
            messages.success(self.request,f"OTP has been sent to {user.email}")
            return redirect ("accounts:otp_verify")
        except Exception as e:
            logger.exception("Signup failed: %s", str(e))
            messages.error(self.request,"Something went wrong while creating your account . Please try again.")
            return self.form_invalid(form)
    
class OtpVerifyView(generic.FormView):
    template_name = "otp_verify.html"
    form_class = OtpForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("signup_user_id"):
            return redirect ("accounts:signup")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user_id = self.request.session.get("signup_user_id")
        user = get_object_or_404(CustomUser,id=user_id)
        otp  = form.cleaned_data.get("otp")

        success , message = OTPService.verify_otp(otp,user)
        if success:
            login(self.request, user)
            messages.success(self.request, "OTP verified successfully.")
            self.request.session.pop("signup_user_id",None)
            return redirect("article:home")
        form.add_error(None, message)
        return self.form_invalid(form)
    
class ResendOtpView(View):
    def post(self,request):
        user_id = request.session.get("signup_user_id")
        if not user_id:
            return redirect ("accounts:signup")
        user = get_object_or_404(CustomUser,id=user_id)
        can_resend , message = OTPService.can_resend_otp(user)
        if not can_resend:
            messages.error(request, message)
            return redirect("accounts:otp_verify")
        OTPService.create_and_send_otp(user)
        return redirect("accounts:otp_verify")
    
class LoginView(View):
    def get(self,request):
        form = LoginForm()
        return render (request,"login.html",{"form":form})
    
    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request,email=email,password=password)
            if user is None:
                form.add_error(None, "Invalid email or password")
                return render(request, "login.html", {"form": form})
            if not user.is_active:
                form.add_error(None, "Account not verified. Please complete OTP verification.")
                return render(request, "login.html", {"form": form})
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("article:home")

class LogoutView(View):
    def get(self, request):
        return redirect("article:home")
    def post(self,request):
        if request.user.is_authenticated:
            logout(request)
        messages.success(request,"Logout Succesfully")
        return redirect ("article:home")
    
class PasswordresetView(PasswordResetView):
    template_name = "password_reset.html"
    form_class = CustomPasswordResetForm
    email_template_name = "password_reset_email.txt"
    subject_template_name = "password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        self.request.session["password_reset"] = True
        return super().form_valid(form)

class PasswordresetDoneView(PasswordResetDoneView):
    template_name = "password_reset_done.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset"):
            return redirect ("accounts:password_reset")
        request.session.pop("password_reset",None)
        return super().dispatch(request, *args, **kwargs)

class PasswordresetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    form_class = CustomPasswordForm
    success_url  = reverse_lazy("accounts:password_reset_complete")

    def form_valid(self, form):
        self.request.session["password_reset_confirm"] = True
        return super().form_valid(form)

class PasswordresetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset_confirm"):
            return redirect ("accounts:login")
        request.session.pop("password_reset_confirm",None)
        return super().dispatch(request, *args, **kwargs)

class ProfileDetailView(LoginRequiredMixin,generic.DetailView):
    template_name = "profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset = None):
        return Profile.objects.select_related("user").filter(user=self.request.user).first()
    
class ProfileUpdateView(LoginRequiredMixin,View):
    def get(self,request):
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render (request,"profile_update.html",{"user_form":user_form,"profile_form":profile_form})
    def post(self,request):
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = ProfileForm(request.POST,request.FILES,instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Profile Updated Successfully")
            return redirect ("accounts:profile_detail")
        return render (request,"profile_update.html",{"user_form":user_form,"profile_form":profile_form})
    
class EmailUpdateView(LoginRequiredMixin,View):
    def get(self,request):
        form = EmailForm(instance=request.user)
        return render (request,"email_update.html",{"form":form})
    def post(self,request):
        user = request.user
        old_email = user.email
        form = EmailForm(request.POST,instance=user)
        if form.is_valid():
            new_email = form.cleaned_data.get("email")
            if new_email != old_email:
                user.email = old_email
                user.pending_email = new_email
                user.save()
                OTPService.create_and_send_email_otp(user)
                messages.success(request,f"An Email verification OTP is sent to {new_email}")
                self.request.session["email_user_id"] = user.id
                return redirect ("accounts:email_otp_verify")
        return render (request,"email_update.html",{"form":form})
    
class EmailOTPVerifyView(LoginRequiredMixin,generic.FormView):
    template_name = "email_otp_verify.html"
    form_class = EmailOtpForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("email_user_id"):
            return redirect ("accounts:email_update")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_id = self.request.session.get("email_user_id")
        user = get_object_or_404(CustomUser,id=user_id)
        otp = form.cleaned_data.get("otp")

        success , message = OTPService.verify_email_otp(otp,user)

        if success:
            messages.success(self.request,"Email Updated Successfully")
            self.request.session.pop("email_user_id",None)
            return redirect ("accounts:profile_detail")
        form.add_error(None,message)
        return self.form_invalid(form)

class EmailResendOTPView(LoginRequiredMixin,View):
    def post(self,request):
        user_id = request.session.get("email_user_id")
        if not user_id:
            return redirect ("accounts:email_update")
        user = get_object_or_404(CustomUser,id=user_id)
        can_resend , message = OTPService.can_resend_otp(user)
        if not can_resend:
            messages.error(request,message)
            return redirect ("accounts:email_otp_verify")
        OTPService.create_and_send_email_otp(user)
        messages.success(request, f"An New OTP is send to {user.pending_email}")
        return redirect("accounts:email_otp_verify")

class PasswordchangeView(LoginRequiredMixin,PasswordChangeView):
    template_name = "password_change.html"
    form_class = CustomPasswordForm
    success_url = reverse_lazy("accounts:password_change_done")

    def form_valid(self, form):
        self.request.session["password_change_done"] = True
        return super().form_valid(form)
    
class PasswordchangeDoneView(LoginRequiredMixin,PasswordChangeDoneView):
    template_name = "password_change_done.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_change_done"):
            return redirect ("accounts:password_change")
        request.session.pop("password_change_done",None)
        return super().dispatch(request, *args, **kwargs)
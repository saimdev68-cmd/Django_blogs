from django.urls import path
from .views import (
    SignUpView,
    LoginView,
    OtpVerifyView,
    LogoutView,
    PasswordresetView,
    PasswordresetDoneView,
    PasswordresetCompleteView,
    PasswordresetConfirmView,
    ProfileDetailView,
    ProfileUpdateView,
    ResendOtpView,
    EmailUpdateView,
    EmailOTPVerifyView,
    EmailResendOTPView,
    PasswordchangeView,
    PasswordchangeDoneView
)

app_name = "accounts"

urlpatterns = [
    path("signup/",SignUpView.as_view(),name="signup"),
    path("login/",LoginView.as_view(),name="login"),
    path("otp/verify/",OtpVerifyView.as_view(),name="otp_verify"),
    path("otp/resend/",ResendOtpView.as_view(),name="otp_resend"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("password/reset/",PasswordresetView.as_view(),name="password_reset"),
    path("password/reset/done/",PasswordresetDoneView.as_view(),name="password_reset_done"),
    path("reset/<uidb64>/<token>/",PasswordresetConfirmView.as_view(),name="password_reset_confirm"),
    path("reset/done/",PasswordresetCompleteView.as_view(),name="password_reset_complete"),
    path("profile/detail/",ProfileDetailView.as_view(),name="profile_detail"),
    path("profile/update/",ProfileUpdateView.as_view(),name="profile_update"),
    path("email/update/",EmailUpdateView.as_view(),name="email_update"),
    path('email/otp/verify/',EmailOTPVerifyView.as_view(),name="email_otp_verify"),
    path('email/otp/resend/',EmailResendOTPView.as_view(),name="email_otp_resend"),
    path("password/change/",PasswordchangeView.as_view(),name="password_change"),
    path("password/change/done/",PasswordchangeDoneView.as_view(),name="password_change_done")
]

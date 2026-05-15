from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    pending_email = models.EmailField(null=True,blank=True)
    otp = models.CharField(max_length=255,null=True,blank=True)
    otp_created_at = models.DateTimeField(null=True,blank=True)
    otp_block_time = models.DateTimeField(null=True,blank=True)
    otp_attempt = models.PositiveIntegerField(default=0)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="profile")
    name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to="profile/",default="default.png")

    def __str__(self):
        return self.name
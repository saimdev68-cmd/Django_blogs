from django.contrib import admin
from .models import CustomUser , Profile

# Register your models here.

class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]
    list_display = ["email","username","is_active","is_staff"]

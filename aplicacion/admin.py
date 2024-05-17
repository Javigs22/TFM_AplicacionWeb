from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import RegisterForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = RegisterForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "verified",
        "is_staff",
    ]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("verified",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("verified",)}),)
admin.site.register(CustomUser, CustomUserAdmin)
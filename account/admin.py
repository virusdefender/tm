# coding=utf-8
from django.contrib import admin
from .models import User, LoginLog, PasswordRecoverySMSLog


class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "phone"]
    list_filter = ["is_staff", "is_superuser"]


class SecurityAdmin(admin.ModelAdmin):
    list_display = ["user", "last_sms_time", "login_failure_number"]


admin.site.register(User, UserAdmin)
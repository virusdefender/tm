# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser

from shop.models import UserGroup


class User(AbstractUser):
    phone = models.CharField(max_length=12, blank=True, null=True)
    score = models.FloatField(default=0)
    sex = models.CharField(max_length=3, blank=True, null=True)
    default_shop_id = models.IntegerField(blank=True, null=True)
    group = models.ForeignKey(UserGroup, blank=True, null=True, help_text=u"用户分组")
    tags = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, default="user")

    class Meta:
        db_table = "user"


class PasswordRecoveryLog(models.Model):
    """发送密码恢复短信的记录
    """
    user = models.ForeignKey(User)
    send_time = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=10)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "password_recovery_log"


class LoginLog(models.Model):
    """用户登陆记录
    """
    user_name = models.CharField(max_length=30)
    time = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    # status=True表示密码正确 False表示密码错误
    status = models.CharField(max_length=30)

    class Meta:
        db_table = "login_log"
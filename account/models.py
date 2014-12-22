# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=12, blank=True, null=True)
    score = models.FloatField(default=0)
    sex = models.CharField(max_length=3, blank=True, null=True)
    default_shop_id = models.IntegerField(blank=True, null=True)


class PasswordRecoveryLog(models.Model):
    """发送密码恢复短信的记录
    """
    user = models.ForeignKey(User)
    send_time = models.DateTimeField(auto_now_add=True)
    code = models.CharField()
    status = models.BooleanField(default=True)


class LoginLog(models.Model):
    """用户登陆记录
    """
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    # status=True表示密码正确 False表示密码错误
    status = models.BooleanField()

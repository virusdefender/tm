# coding=utf-8
from django.db import models

from account.models import User


class SignUpLog(models.Model):
    user = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        db_table = "signup_log"

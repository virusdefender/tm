# coding=utf-8
import xadmin

from .models import SignUpLog


class SignUpLogAdmin(object):
    list_display = ["user", "create_time"]


xadmin.site.register(SignUpLog, SignUpLogAdmin)
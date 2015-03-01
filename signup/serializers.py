# coding=utf-8
from rest_framework import serializers

from .models import SignUpLog


class SignUpLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUpLog
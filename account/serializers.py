# coding=utf-8
from rest_framework import serializers

from .models import User


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
    captcha = serializers.CharField(max_length=4, required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "phone", "score", "gender", "is_vip"]


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=30)
    new_password = serializers.CharField(min_length=6, max_length=30)
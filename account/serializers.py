# coding=utf-8
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
    captcha = serializers.CharField(max_length=4, required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
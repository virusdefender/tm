# coding=utf-8
from rest_framework import serializers

from .models import Shop, Category, Product, Order


class CategorySerializer(serializers.Serializer):
    pass
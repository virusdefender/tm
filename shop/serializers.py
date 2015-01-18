# coding=utf-8
from rest_framework import serializers

from .models import Shop, Category, Product, Order


class CategorySerializer(serializers.ModelSerializer):
    child_category = serializers.SerializerMethodField("_get_child_category")

    class Meta:
        model = Category
        exclude = ["parent_category", "sort_index"]

    def _get_child_category(self, obj):
        return CategorySerializer(obj.child_category.all().order_by("sort_index"), many=True).data
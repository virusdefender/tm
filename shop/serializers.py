# coding=utf-8
import json

from rest_framework import serializers

from .models import Shop, Category, Product, Order


class ShopSerializer(serializers.ModelSerializer):
    # delivery_time = serializers.SerializerMethodField("_get_shop_delivery_time")
    banner = serializers.SerializerMethodField("_get_shop_banner")

    class Meta:
        model = Shop
        exclude = ["admin", "create_time", "status", "delivery_time"]

    def _get_shop_delivery_time(self, obj):
        return obj.get_delivery_time

    def _get_shop_banner(self, obj):
        if obj.banner:
            return json.loads(obj.banner)
        else:
            return []


class CategorySerializer(serializers.ModelSerializer):
    child_category = serializers.SerializerMethodField("_get_child_category")

    class Meta:
        model = Category
        exclude = ["parent_category", "sort_index"]

    def _get_child_category(self, obj):
        return CategorySerializer(obj.child_category.all().order_by("-sort_index"), many=True).data


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ["shop", "origin_price", "total_num", "create_time", "last_modify_time", "status", "sort_index"]
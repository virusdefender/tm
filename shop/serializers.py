# coding=utf-8
import json

from rest_framework import serializers

from .models import Shop, Category, Product, Order


class ShopSerializer(serializers.ModelSerializer):
    delivery_time = serializers.SerializerMethodField("_get_shop_delivery_time")
    banner = serializers.SerializerMethodField("_get_shop_banner")

    class Meta:
        model = Shop
        exclude = ["admin", "create_time", "status"]

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
    # cart_num = serializers.SerializerMethodField("_cart_num")

    def _cart_num(self, obj):
        return 0

    class Meta:
        model = Product
        exclude = ["shop", "origin_price", "total_num", "create_time", "last_modify_time", "status", "sort_index"]


class ShoppingCartOperationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    number = serializers.IntegerField()
    shop_id = serializers.IntegerField()


class CreateOrderSerializer(serializers.Serializer):
    pay_method = serializers.ChoiceField(choices=(("COD", "COD"), ("alipay", "alipay")))
    name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=11, min_length=11)
    address = serializers.CharField(max_length=40)
    remark = serializers.CharField(max_length=40, required=False)
    shop_id = serializers.IntegerField()
    delivery_time = serializers.WritableField()
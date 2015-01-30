# coding=utf-8
import json

from rest_framework import serializers

from account.models import User
from .models import Shop, Category, Product, Order, OrderLog, OrderProduct


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


class ShoppingCartDeleteSerializer(serializers.Serializer):
    shop_id = serializers.IntegerField()
    products = serializers.WritableField()


class CreateOrderSerializer(serializers.Serializer):
    pay_method = serializers.ChoiceField(choices=(("COD", "COD"), ("alipay", "alipay")))
    name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=11, min_length=11)
    address = serializers.CharField(max_length=40)
    remark = serializers.CharField(max_length=40, required=False)
    shop_id = serializers.IntegerField()
    delivery_time = serializers.WritableField()


class OrderShopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "name"]
        model = Shop


class OrderUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "username"]
        model = User


class OrderLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLog
        exclude = ["order"]


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        exclude = ["order", "origin_price"]


class OrderSerializer(serializers.ModelSerializer):
    shop = OrderShopSerializer()
    user = OrderUserSerializer()
    delivery_time = serializers.SerializerMethodField("_covert_delivery_time")
    order_logs = serializers.SerializerMethodField("_get_order_logs")
    order_products = serializers.SerializerMethodField("_get_order_products")

    class Meta:
        model = Order
        exclude = ["address_category", "source", "is_first"]

    def _covert_delivery_time(self, obj):
        return json.loads(obj.delivery_time)

    def _get_order_logs(self, obj):
        return OrderLogSerializer(OrderLog.objects.filter(order=obj), many=True).data

    def _get_order_products(self, obj):
        return OrderProductSerializer(OrderProduct.objects.filter(order=obj), many=True).data
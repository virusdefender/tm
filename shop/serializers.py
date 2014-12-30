# coding=utf-8
from rest_framework import serializers

from .models import Shop, Category, Product


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name",
                  "contact_information",
                  "min_money",
                  "announcement",
                  "personalized_recommendation",
                  "status"]


class CategorySerializer(serializers.ModelSerializer):
    child_category = serializers.SerializerMethodField("_get_child_category")

    class Meta:
        model = Category

    def _get_child_category(self, obj):
        return CategorySerializer(obj.child_category.all().order_by("sort_index"), many=True).data


class ProductSerializer(serializers.ModelSerializer):
    child_product = serializers.SerializerMethodField("_get_child_product")
    cart_num = serializers.SerializerMethodField("_get_product_cart_num")

    class Meta:
        model = Product

    def _get_child_product(self, obj):
        return ProductSerializer(obj.child_product.all().order_by("sort_index"), many=True).data

    def _get_product_cart_num(self, obj):
        return 0


class ShoppingCartProductSerializer(serializers.ModelSerializer):
    cart_num = serializers.SerializerMethodField("_get_product_cart_num")

    class Meta:
        model = Product

    def _get_product_cart_num(self, obj):
        return obj._cart_num


class ProductCartOperationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    operation = serializers.IntegerField()
    source = serializers.CharField(max_length=30)
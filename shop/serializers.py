# coding=utf-8
from rest_framework import serializers

from .models import Shop, Category, Product


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name",
                  "contact_information",
                  "first_order_min_money",
                  "ordinary_min_money",
                  "announcement",
                  "personalized_recommendation", "status"]


class CategorySerializer(serializers.ModelSerializer):
    child_category = serializers.SerializerMethodField("_get_child_category")

    class Meta:
        model = Category

    def _get_child_category(self, obj):
        return CategorySerializer(obj.child_category.all().order_by("sort_index"), many=True).data


class ProductSerializer(serializers.ModelSerializer):
    child_product = serializers.SerializerMethodField("_get_child_product")

    class Meta:
        model = Product

    def _get_child_product(self, obj):
        return ProductSerializer(obj.child_product.all().order_by("sort_index"), many=True).data
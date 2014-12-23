# coding=utf-8
from rest_framework import serializers

from .models import Shop, Category


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name",
                  "contact_information",
                  "first_order_min_money",
                  "ordinary_min_money",
                  "announcement",
                  "personalized_recommendation"]


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30)
    is_index = serializers.BooleanField()
    child_category = serializers.SerializerMethodField("_get_child_category")

    def _get_child_category(self, obj):
        return CategorySerializer(obj.child_category.all(), many=True).data
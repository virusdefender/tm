# coding=utf-8
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Shop, Product, Category
from .serializers import ShopSerializer, CategorySerializer


class ShopView(APIView):
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return Response(data={"status": "error"})
        return Response(data=ShopSerializer(shop).data)


class CategoryView(APIView):
    def get(self, request):
        category = Category.objects.filter(parent_category__isnull=True).order_by("sort_index")
        return Response(data=CategorySerializer(category, many=True).data)

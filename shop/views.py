# coding=utf-8
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.shortcuts import http_400_response
from .models import Shop, Category, Product
from .serializers import CategorySerializer, ShopSerializer, ProductSerializer


class ShopView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop_id", None)
        if shop_id:
            try:
                shop = Shop.objects.get(pk=shop_id)
                return Response(data=ShopSerializer(shop).data)
            except Shop.DoesNotExist:
                return http_400_response("Shop does not exist")
        else:
            return Response(ShopSerializer(Shop.objects.all(), many=True).data)


class CategoryView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop_id", -1)
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return http_400_response("Shop does not exist")
        return Response(data=CategorySerializer(Category.objects.filter(shop=shop, parent_category__isnull=True).order_by("-sort_index"), many=True).data)


class ProductView(APIView):
    def get(self, request):
        category_id = request.GET.get("category_id", -1)
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return http_400_response("Category does not exist")
        return Response(data=ProductSerializer(category.get_category_product(), many=True).data)
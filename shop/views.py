# coding=utf-8
from django.template.response import TemplateResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Shop, Product, Category
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer


class ShopView(APIView):
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return Response(data={"status": "error"})
        data_format = request.GET.get("format", None)
        if data_format:
            return render()
            return Response(data=ShopSerializer(shop).data)
        else:
            return TemplateResponse(request, "shop/shop_index.html")


class CategoryView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop", -1)
        category = Category.objects.filter(shop=shop_id, parent_category__isnull=True).order_by("sort_index")
        return Response(data=CategorySerializer(category, many=True).data)


class ProductView(APIView):
    def get(self, request):
        category_id = request.GET.get("category", -1)
        product = Product.objects.filter(category=category_id, parent_product__isnull=True).order_by("sort_index")
        return Response(data=ProductSerializer(product, many=True).data)
# coding=utf-8
import json
from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser

from rest_framework.views import APIView
from rest_framework.response import Response

from log.models import CategoryClickLog, ShoppingCartOperationLog

from .models import Shop, Product, Category
from .serializers import (ShopSerializer, CategorySerializer, ProductSerializer,
                          ProductCartOperationSerializer, ShoppingCartProductSerializer)
from .shopping_cart import ShoppingCart


class ShopView(APIView):
    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return Response(data={"status": "error"})
        data_format = request.GET.get("format", None)
        if data_format:
            return Response(data=ShopSerializer(shop).data)
        else:
            return render(request, "shop/shop_index.html")


class CategoryView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop", -1)
        category = Category.objects.filter(shop=shop_id, parent_category__isnull=True).order_by("sort_index")
        return Response(data=CategorySerializer(category, many=True).data)


class ProductView(APIView):
    def get(self, request):
        category_id = request.GET.get("category", -1)
        data = {}
        data["category_id"] = category_id
        if isinstance(request.user, AnonymousUser):
            data["session_id"] = request.session._session_key
        else:
            data["user"] = request.user
        CategoryClickLog.objects.create(**data)

        product = Product.objects.filter(category=category_id, parent_product__isnull=True).order_by("sort_index")
        return Response(data=ProductSerializer(product, many=True).data)


class ShoppingCartView(APIView):
    def get(self, request):
        operation = request.GET.get("operation", "get_cart_page")

        if operation == "get_cart_num":
            product_list = request.GET.get("product_list", [])
            num_list = []
            try:
                l = json.loads(product_list)
            except Exception:
                return Response(data=num_list)
            s = ShoppingCart(request)
            return Response(data=s.get_product_cart_num(l))

        elif operation == "get_cart_page":
            return render(request, "shop/shopping_cart.html")

        elif operation == "get_cart_data":
            s = ShoppingCart(request)
            return Response(data=ShoppingCartProductSerializer(s.shopping_cart_data, many=True).data)

    def post(self, request):
        serializer = ProductCartOperationSerializer(data=request.DATA)
        if serializer.is_valid():
            s = ShoppingCart(request)
            data = serializer.data

            log_data = {}
            log_data["product_id"] = data["product_id"]
            log_data["source"] = data["source"]

            if isinstance(request.user, AnonymousUser):
                log_data["session_id"] = request.session._session_key
            else:
                log_data["user"] = request.user

            if data["operation"] > 0:
                log_data["operation"] = "+1"
                self.request.session["shopping_cart"] = s.add_to_cart(data["product_id"])
            else:
                log_data["operation"] = "-1"
                self.request.session["shopping_cart"] = s.del_from_cart(data["product_id"])

            ShoppingCartOperationLog.objects.create(**log_data)
        return Response(data={"status": "success"})


class OrderView(APIView):
    def get(self, request):
        return render(request, "shop/submit_order.html")
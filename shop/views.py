# coding=utf-8
import json
from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt

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


class PayView(APIView):
    def get(self, request):
        return render(request, "shop/pay.html")

    def post(self, request):
        print request.DATA
        import pingpp
        pingpp.api_key = 'sk_test_P4aDSG8CeHG0P0W1iPCKKun1'
        ch = pingpp.Charge.create(
            order_no='fsd23rfwef',
            amount=1,
            app=dict(id='app_HGqP44OW5un1Gyzz'),
            channel=request.DATA["channel"],
            currency='cny',
            client_ip='192.26.2.12',
            subject='test-subject',
            body='test-body',
            extra={"success_url": "http://127.0.0.1:8000/pay/success/"}
          )
        return Response(data=ch)
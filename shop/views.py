# coding=utf-8
import json
import time

from decimal import Decimal

import pingpp

from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

from utils.shortcuts import http_400_response
from .models import Shop, Category, Product, Order, AddressCategory
from .serializers import (CategorySerializer, ShopSerializer, ProductSerializer,
                          ShoppingCartOperationSerializer, CreateOrderSerializer)
from .shopping_cart import ShoppingCart


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


class ShoppingCartView(APIView):
    def get(self, request):
        print request.META
        shopping_cart_id = request.session.get("shopping_cart_id", None)
        if not shopping_cart_id:
            shopping_cart = ShoppingCart()
        else:
            shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

        try:
            shop_id = int(request.GET.get("shop_id", -1))
        except Exception as e:
            return http_400_response(e)

        data = request.GET.get("data", None)
        if not data:
            product_list = []
            for item in shopping_cart._data(shop_id):
                product_list.append({"product": ProductSerializer(item["product"]).data, "number": item["number"]})
            response_data = {"total": shopping_cart.total(shop_id), "products": product_list}
            return Response(data=response_data)

        elif data == "cart_num":
            product_list = request.GET.get("product_list", json.dumps([]))
            try:
                product_list = json.loads(product_list)
            except Exception:
                return http_400_response("Failed to parse product list")

            return Response(data=shopping_cart.get_product_cart_number(product_list, shop_id))

        elif data == "total":
            return Response(data=shopping_cart.total(shop_id))

    def post(self, request):
        shopping_cart_id = request.session.get("shopping_cart_id", None)
        print shopping_cart_id
        if not shopping_cart_id:
            shopping_cart = ShoppingCart()
            request.session["shopping_cart_id"] = shopping_cart.key
        else:
            shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

        serializer = ShoppingCartOperationSerializer(data=request.DATA)

        if serializer.is_valid():
            data = serializer.data
            if data["number"] == 0:
                return http_400_response("Error number")

            try:
                Product.objects.get(pk=data["product_id"], status=True)
            except Product.DoesNotExist:
                return http_400_response("Product does not exist")

            if data["number"] >= 1:
                shopping_cart.add_to_cart(data["product_id"], data["number"])
            else:
                shopping_cart.del_from_cart(data["product_id"], data["number"])

            return Response(data=shopping_cart.total(data["shop_id"]))
        else:
            return http_400_response(serializer.errors)


class ShopIndexView(APIView):
    def get(self, request, shop_id):
        try:
            Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return render(request, "error.html")
        return render(request, "shop/shop_index.html", {"shop_id": shop_id})


class ShoppingCartIndexView(APIView):
    def get(self, request):
        return render(request, "shop/shopping_cart.html")


def get_address_category(address, shop_id):
    if not address:
        return None
    for item in AddressCategory.objects.filter(shop=shop_id):
        for keyword in item.keywords.split(";"):
            if keyword in address:
                return item
    return None


class OrderIndexView(APIView):
    def get(self, request):
        data = request.GET.get("data", None)
        if not data:
            return render(request, "shop/submit_order.html")
        else:
            return Response(data={"name": "name", "phone": "11111111111", "address": "address"})

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            try:
                shop = Shop.objects.get(pk=data["shop_id"])
            except Shop.DoesNotExist:
                return http_400_response(u"商店不存在")
            shopping_cart_id = request.session.get("shopping_cart_id", None)
            if not shopping_cart_id:
                return http_400_response(u"购物车为空，请重新添加")
            else:
                shopping_cart = ShoppingCart(shopping_cart_id)

            shopping_cart_data = shopping_cart.total(shop.id)
            if shopping_cart_data["total_price"] <= Decimal("0"):
                return http_400_response(u"购物车为空。请重新添加")
            try:
                delivery_time = json.dumps(data["delivery_time"])
            except Exception as e:
                return http_400_response(e)

            user = request.user

            is_first = Order.objects.filter(user=user, shop=shop).exists()

            address_category = get_address_category(data["address"], shop.id)
            if data["pay_method"] == "alipay":
                order = Order.objects.create(name=data["name"], phone=data["phone"],
                                             address=data["address"], remark=data["remark"],
                                             delivery_time=delivery_time, shop=shop,
                                             pay_method=data["pay_method"], is_first=is_first, user=user,
                                             address_category=address_category,
                                             alipay_amount=shopping_cart_data["total_price"],
                                             total_price=shopping_cart_data["total_price"])
            else:
                order = Order.objects.create(name=data["name"], phone=data["phone"],
                                             address=data["address"], remark=data["remark"],
                                             delivery_time=delivery_time, shop=shop,
                                             pay_method=data["pay_method"], is_first=is_first, user=user,
                                             address_category=address_category,
                                             total_price=shopping_cart_data["total_price"])

            if data["pay_method"] == "alipay":
                # sk_live_efHSmHz9G0iLGqPmPS5OynXD
                # sk_test_P4aDSG8CeHG0P0W1iPCKKun1
                pingpp.api_key = 'sk_live_efHSmHz9G0iLGqPmPS5OynXD'
                ch = pingpp.Charge.create(
                    order_no=order.id,
                    amount=int(order.alipay_amount * Decimal("100")),
                    app=dict(id='app_HGqP44OW5un1Gyzz'),
                    channel='alipay_wap',
                    currency='cny',
                    client_ip='127.0.0.1',
                    subject=u'天目订单',
                    body='test-body',
                    extra={"success_url": "https://tmqdu.com/pay/success/",
                           "cancel_url": "https://tmqdu.com/pay/failed/"}
                )
                return Response(data=ch)
            else:
                return Response(data="not implement")

        else:
            return http_400_response(serializer.errors)




class PayResultView(APIView):
    def get(self, request, result):
        return render(request, "shop/pay_result.html", {"result": result})
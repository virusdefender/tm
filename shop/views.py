# coding=utf-8
import json
import time
import hashlib
import random
import uuid
import logging

from decimal import Decimal

import pingpp

from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework.views import APIView

from utils.decorators import login_required, never_ever_cache
from utils.shortcuts import http_400_response, decimal_round, paginate
from .models import Shop, Category, Product, Order, AddressCategory
from .serializers import (CategorySerializer, ShopSerializer, ProductSerializer,
                          ShoppingCartOperationSerializer, CreateOrderSerializer,
                          ShoppingCartDeleteSerializer, OrderSerializer)
from .shopping_cart import ShoppingCart


def rand_key():
    return hashlib.md5(str(time.time())).hexdigest()


class ShopAPIView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop_id", None)
        if shop_id:
            # 返回单个商店信息
            try:
                shop = Shop.objects.get(pk=shop_id)
                return Response(data=ShopSerializer(shop).data)
            except Shop.DoesNotExist:
                return http_400_response("Shop does not exist")
        else:
            # 返回商店列表
            return Response(ShopSerializer(Shop.objects.all(), many=True).data)


class CategoryAPIView(APIView):
    def get(self, request):
        # 返回这个商店所有的分类
        shop_id = request.GET.get("shop_id", -1)
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return http_400_response("Shop does not exist")
        return Response(data=CategorySerializer(Category.objects.filter(shop=shop, parent_category__isnull=True).order_by("-sort_index"), many=True).data)


class ProductAPIView(APIView):
    def get(self, request):
        # 获取这个分类下的所有的商品
        category_id = request.GET.get("category_id", None)
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                return http_400_response("Category does not exist")
            return Response(data=ProductSerializer(category.get_category_product(), many=True).data)
        keyword = request.GET.get("keyword", None)
        shop_id = request.GET.get("shop_id", -1)
        if keyword:
            return Response(data=ProductSerializer(Product.objects.filter(name__icontains=keyword, shop=shop_id), many=True).data)
        return []


class ShoppingCartAPIView(APIView):
    @method_decorator(never_ever_cache)
    def get(self, request):
        shopping_cart_id = request.session.get("shopping_cart_id", None)
        if not shopping_cart_id:
            shopping_cart = ShoppingCart(rand_key())
        else:
            shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

        try:
            shop_id = int(request.GET.get("shop_id", -1))
            shop = Shop.objects.get(pk=shop_id)
        except Exception as e:
            return http_400_response(e)

        data = request.GET.get("data", None)

        if not data:
            # 获取购物车所有信息 比如商品信息 总价 总数量 运费等
            products_info = shopping_cart.total(shop_id, request.user)
            if not products_info:
                return http_400_response("Shop does not exist")

            for item in products_info["products"]:
                item["product"] = ProductSerializer(item["product"]).data
            return Response(data=products_info)

        elif data == "cart_num":
            # 返回指定商品的数量
            product_list = request.GET.get("product_list", json.dumps([]))
            try:
                product_list = json.loads(product_list)
            except Exception:
                return http_400_response("Failed to parse product list")

            return Response(data=shopping_cart.get_product_cart_number(product_list, shop_id))

    @method_decorator(never_ever_cache)
    def post(self, request):
        # 添加或减少商品数量
        shopping_cart_id = request.session.get("shopping_cart_id", None)
        if not shopping_cart_id:
            shopping_cart = ShoppingCart(rand_key())
            request.session["shopping_cart_id"] = shopping_cart.key
        else:
            shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

        serializer = ShoppingCartOperationSerializer(data=request.DATA)

        if serializer.is_valid():
            data = serializer.data

            try:
                shop = Shop.objects.get(pk=data["shop_id"])
            except Shop.DoesNotExist:
                return http_400_response("Shop does not exist")

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

            data = shopping_cart.total(shop.id, request.user)
            data.pop("products")

            return Response(data=data)
        else:
            return http_400_response(serializer.errors)

    @method_decorator(never_ever_cache)
    def delete(self, request):
        serializer = ShoppingCartDeleteSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            try:
                shop = Shop.objects.get(pk=data["shop_id"])
            except Shop.DoesNotExist:
                return http_400_response("Shop does not exist")

            shopping_cart_id = request.session.get("shopping_cart_id", None)
            if not shopping_cart_id:
                shopping_cart = ShoppingCart(rand_key())
                request.session["shopping_cart_id"] = shopping_cart.key
            else:
                shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

            for item in data["products"]:
                shopping_cart.del_from_cart(item, -10000)
            cart_data = shopping_cart.total(shop.id, request.user)
            cart_data.pop("products")
            return Response(data=cart_data)
        else:
            return http_400_response(serializer.errors)


class ShopIndexPageView(APIView):
    def get(self, request, shop_id):
        try:
            Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return render(request, "error.html")
        return render(request, "shop/shop_index.html", {"shop_id": shop_id})


class ShoppingCartPageView(APIView):
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


class SubmitOrderPageView(APIView):
    @method_decorator(never_ever_cache)
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?from=/order/")
        return render(request, "shop/submit_order.html")


def pay(request, order):
    # sk_live_efHSmHz9G0iLGqPmPS5OynXD
    # sk_test_P4aDSG8CeHG0P0W1iPCKKun1
    pingpp.api_key = 'sk_test_P4aDSG8CeHG0P0W1iPCKKun1'

    real_ip = request.META.get("HTTP_X_REAL_IP", "127.0.0.1")

    is_app = request.META.get("HTTP_APPVERSION", None)

    if not is_app:

        ch = pingpp.Charge.create(
            order_no=order.alipay_order_id,
            amount=1, #int(order.alipay_amount * Decimal("100")),
            app=dict(id='app_HGqP44OW5un1Gyzz'),
            channel='alipay_wap',
            currency='cny',
            client_ip=real_ip,
            subject=u'天目订单',
            body='test-body',
            extra={"success_url": "https://tmqdu.com/pay/success/",
                   "cancel_url": "https://tmqdu.com/pay/failed/"}
        )
    else:
        ch = pingpp.Charge.create(
            order_no=order.alipay_order_id,
            amount=1, #int(order.alipay_amount * Decimal("100")),
            app=dict(id='app_HGqP44OW5un1Gyzz'),
            channel='alipay',
            currency='cny',
            client_ip=real_ip,
            subject=u'天目订单',
            body='test-body',
            )

    return {"pay_method": "alipay", "order_id": order.id, "charge": ch}


class OrderRepayAPIView(APIView):
    @method_decorator(never_ever_cache)
    @login_required
    def post(self, request):
        data = request.DATA
        try:
            order = Order.objects.get(user=request.user, pk=data.get("order_id", -1))
        except Order.DoesNotExist:
            return http_400_response("Order does not exist")
        if not (order.payment_status == 0 and order.pay_method == "alipay"):
            return http_400_response("Error order type")
        return Response(data=pay(request, order))


class OrderAPIView(APIView):
    @method_decorator(never_ever_cache)
    @login_required
    def post(self, request):
        # 创建订单
        with transaction.atomic():
            serializer = CreateOrderSerializer(data=request.DATA)
            if serializer.is_valid():
                data = serializer.data
                try:
                    shop = Shop.objects.get(pk=data["shop_id"])
                except Shop.DoesNotExist:
                    return http_400_response(u"商店不存在", 1)

                shopping_cart_id = request.session.get("shopping_cart_id", None)

                if not shopping_cart_id:
                    return http_400_response(u"购物车为空，请重新添加", 1)
                else:
                    shopping_cart = ShoppingCart(shopping_cart_id)

                shopping_cart_data = shopping_cart.total(shop.id, request.user)

                # 购物车中没有商品
                if shopping_cart_data["total_price"] <= Decimal("0"):
                    return http_400_response(u"购物车为空。请重新添加", 1)

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
                                                 alipay_order_id=hashlib.md5(str(time.time()) + str(uuid.uuid1())).hexdigest(),
                                                 delivery_time=delivery_time, shop=shop,
                                                 pay_method="alipay", is_first=is_first, user=user,
                                                 address_category=address_category,
                                                 total_price=shopping_cart_data["total_price"],
                                                 freight=shopping_cart_data["freight"],
                                                 origin_price=shopping_cart_data["origin_price"],
                                                 vip_discount_amount=shopping_cart_data["vip_discount_amount"],
                                                 activity_discount_amount=shopping_cart_data["activity_discount_amount"]
                                                 )
                else:
                    order = Order.objects.create(name=data["name"], phone=data["phone"],
                                                 address=data["address"], remark=data["remark"],
                                                 delivery_time=delivery_time, shop=shop,
                                                 pay_method="COD", is_first=is_first, user=user,
                                                 address_category=address_category,
                                                 total_price=shopping_cart_data["total_price"],
                                                 freight=shopping_cart_data["freight"],
                                                 origin_price=shopping_cart_data["origin_price"],
                                                 vip_discount_amount=shopping_cart_data["vip_discount_amount"],
                                                 activity_discount_amount=shopping_cart_data["activity_discount_amount"]
                                                 )
                for item in shopping_cart_data["products"]:
                    item["product"].create_order_product(order, item["number"])

                order.create_order_log(u"这里显示订单处理进度1")
                order.create_order_log(u"这里显示订单处理进度2")

                shopping_cart.empty()

                if data["pay_method"] == "alipay":
                    return Response(data=pay(request, order), status=201)
                else:
                    return Response(data={"pay_method": "COD", "order_id": order.id}, status=201)
            else:
                return http_400_response(serializer.errors)

    @method_decorator(never_ever_cache)
    @login_required
    def get(self, request):
        if request.GET.get("data", None) == "history_info":
            return Response(data={"name": "name", "phone": "11111111111", "address": "address"})
        order_id = request.GET.get("order_id", None)
        if order_id:
            try:
                order = Order.objects.get(pk=order_id, user=request.user)
            except Order.DoesNotExist:
                return http_400_response("Order does not exist")
            return Response(data=OrderSerializer(order).data)
        else:
            orders = Order.objects.filter(user=request.user)
            return paginate(request, orders, OrderSerializer)


class PayResultPageView(APIView):
    def get(self, request, result):
        # result 是success 和 failed 的时候 是支付后跳转到这个页面上 result 是notify 的时候是异步通知
        if result not in ["success", "failed"]:
            return render(request, "error.html")
        alipay_order_id = request.GET.get("out_trade_no", None)
        if not alipay_order_id:
            return render(request, "error.html")
        try:
            order = Order.objects.get(alipay_order_id=alipay_order_id, user=request.user)
            return HttpResponseRedirect("/my_order/?order_id=" + str(order.id))
        except Order.DoesNotExist:
            return HttpResponseRedirect("/my_order/")


class PayNotifyAPIView(APIView):
    def post(self, request):
        order_no = request.DATA["order_no"]
        try:
            order = Order.objects.get(alipay_order_id=order_no)
        except Order.DoesNotExist:
            return ""
        order.payment_status = 1
        order.save()
        return Response(data="success")


class OrderListPageView(APIView):
    def get(self, request):
        order_id = request.GET.get("order_id", None)
        if order_id:
            return render(request, "shop/order.html", {"order_id": order_id})
        return render(request, "shop/order_list.html")
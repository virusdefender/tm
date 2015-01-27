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

from rest_framework.response import Response
from rest_framework.views import APIView

from utils.decorators import login_required
from utils.shortcuts import http_400_response
from .models import Shop, Category, Product, Order, AddressCategory
from .serializers import (CategorySerializer, ShopSerializer, ProductSerializer,
                          ShoppingCartOperationSerializer, CreateOrderSerializer)
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
        category_id = request.GET.get("category_id", -1)
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return http_400_response("Category does not exist")
        return Response(data=ProductSerializer(category.get_category_product(), many=True).data)


class ShoppingCartAPIView(APIView):
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
            products_info = shopping_cart.total(shop_id)
            if not products_info:
                return http_400_response("Shop does not exist")

            if request.user.is_authenticated() and request.user.is_vip:
                products_info["discount"] = True
                products_info["after_discount"] = round(products_info["total_price"] * shop.vip_discount, 2)
            else:
                products_info["discount"] = False
                products_info["after_discount"] = products_info["total_price"]

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

            data = shopping_cart.total(data["shop_id"])
            data.pop("products")

            if request.user.is_authenticated() and request.user.is_vip:
                data["discount"] = True
                data["after_discount"] = round(data["total_price"] * shop.vip_discount, 2)
            else:
                data["discount"] = False
                data["after_discount"] = data["total_price"]

            return Response(data=data)
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
    @login_required
    def get(self, request):
        return render(request, "shop/submit_order.html")


class OrderAPIView(APIView):
    @login_required
    def post(self, request):
        logger = logging.getLogger('pay_log')
        logger.debug("test1111111")
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

                shopping_cart_data = shopping_cart.total(shop.id)

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
                                                 pay_method=data["pay_method"], is_first=is_first, user=user,
                                                 address_category=address_category,
                                                 alipay_amount=shopping_cart_data["total_price"],
                                                 total_price=shopping_cart_data["total_price"],
                                                 freight=shopping_cart_data["freight"])
                else:
                    order = Order.objects.create(name=data["name"], phone=data["phone"],
                                                 address=data["address"], remark=data["remark"],
                                                 delivery_time=delivery_time, shop=shop,
                                                 pay_method=data["pay_method"], is_first=is_first, user=user,
                                                 address_category=address_category,
                                                 total_price=shopping_cart_data["total_price"],
                                                 freight=shopping_cart_data["freight"])

                for item in shopping_cart_data["products"]:
                    item["product"].create_order_product(order, item["number"])

                if data["pay_method"] == "alipay":
                    # sk_live_efHSmHz9G0iLGqPmPS5OynXD
                    # sk_test_P4aDSG8CeHG0P0W1iPCKKun1
                    pingpp.api_key = 'sk_live_efHSmHz9G0iLGqPmPS5OynXD'

                    real_ip = request.META.get("HTTP_X_REAL_IP", "127.0.0.1")

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
                    return Response(data={"pay_method": "alipay", "order_id": order.id, "charge": ch}, status=201)
                else:
                    return Response(data={"pay_method": "COD", "order_id": order.id}, status=201)
            else:
                return http_400_response(serializer.errors)

    @login_required
    def get(self, request):
        if request.GET.get("data", None) == "history_info":
            return Response(data={"name": "name", "phone": "11111111111", "address": "address"})


class PayResultPageView(APIView):
    def get(self, request, result):
        # result 是success 和 failed 的时候 是支付后跳转到这个页面上 result 是notify 的时候是异步通知
        if result not in ["success", "failed"]:
            return render(request, "error.html")
        alipay_order_id = request.GET.get("out_trade_no", None)
        if not alipay_order_id:
            return render(request, "error.html")
        try:
            order = Order.objects.get(alipay_order_id=alipay_order_id)
            return HttpResponseRedirect("/my_order/?order_id=" + str(order.id))
        except Order.DoesNotExist:
            return HttpResponseRedirect("/my_order/")

    def post(self, request, result):
        order_no = request.DATA["order_no"]
        try:
            order = Order.objects.get(alipay_order_id=order_no)
        except Order.DoesNotExist:
            return ""
        order.payment_status = 1
        order.save()
        return Response(data="success")
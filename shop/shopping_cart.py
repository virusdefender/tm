# coding=utf-8
import uuid
import hashlib
import json
import time

from decimal import Decimal

import redis

from tm.settings import SHOPPING_CART_REDIS_DB

from .models import Product, Shop
from .serializers import ProductSerializer


class ShoppingCart(object):

    def __init__(self, shopping_cart_key):
        """
        shopping_cart_key 是存储在session 中的标识唯一一个购物车的
        """
        self.key = shopping_cart_key
        self.redis = redis.Redis(db=SHOPPING_CART_REDIS_DB)

        # 过期时间 30天
        self.key_expire_time = 60 * 60 * 24 * 30

        if not self.redis.get(self.key):
            self._set_key_value([])

        # 在 redis 中读取信息
        s = self.redis.get(self.key)
        if s is None:
            self.shopping_cart = []
        else:
            self.shopping_cart = json.loads(s)

    def _set_key_value(self, value):
        """
        在 redis 中设置 key 和 value，更新过期时间
        """
        self.redis.set(self.key, json.dumps(value))
        self.redis.expire(self.key,  self.key_expire_time)

    def add_to_cart(self, product_id, num=1):
        """
        商品加入购物车
        """
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["number"] += num
                item["last_update_time"] = time.time()
                self._set_key_value(self.shopping_cart)
                return

        self.shopping_cart.append({"product_id": product_id, "number": num, "last_update_time": time.time()})
        self._set_key_value(self.shopping_cart)

    def del_from_cart(self, product_id, num=1):
        """
        在购物车中减掉商品
        """
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["number"] += num
                if item["number"] <= 0:
                    self.shopping_cart = [item for item in self.shopping_cart if item["product_id"] != product_id]
                break
        self._set_key_value(self.shopping_cart)
        
    def empty(self):
        """
        清空购物车
        """
        self._set_key_value([])

    def _products(self, shop_id):
        """
        获取购物车中商品列表
        """
        result_list = []
        for item in self.shopping_cart:
            try:
                product = Product.objects.get(shop=shop_id, pk=item["product_id"])
                # 商品下架了  然后就判断一下是什么时间加入购物车的
                if product.status is False:
                    if time.time() - item["last_update_time"] >= 60 * 60 * 10:
                        continue
                result_list.append({"product": product, "number": item["number"]})
            except Product.DoesNotExist:
                continue

        return result_list

    def total(self, shop_id):
        """
        获取购物车中总价，总数量，运费和商品信息
        """
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return None
        result = {"total_number": 0, "total_price": Decimal("0"),
                  "freight": Decimal("0"), "products": self._products(shop.id)}

        for item in result["products"]:
            result["total_number"] += item["number"]
            result["total_price"] += Decimal(item["product"].price) * Decimal(item["number"])

        if shop.freight_line <= result["total_price"]:
            result["freight"] = '0'
        else:
            result["freight"] = shop.freight
            result["total_price"] += result["freight"]

        return result

    def get_product_cart_number(self, product_list, shop_id):
        """
        获取指定的商品的数量
        """
        response_data = []

        for product_id in product_list:
            flag = False
            for item in self._products(shop_id):
                if item["product"].id == product_id:
                    response_data.append(item["number"])
                    flag = True
                    break
            if not flag:
                response_data.append(0)
        return response_data
# coding=utf-8
import uuid
import hashlib
import json
import time

import redis

from tm.settings import SHOPPING_CART_REDIS_DB

from .models import Product, Shop


class ShoppingCart(object):
    def __init__(self, shopping_cart_key=hashlib.md5(str(time.time())).hexdigest()):
        self.key = shopping_cart_key
        self.redis = redis.Redis(db=SHOPPING_CART_REDIS_DB)

        # 过期时间 30天
        self.key_expire_time = 60 * 60 * 24 * 30

        if not self.redis.get(self.key):
            self.set_key_value([])

        # 在 redis 中读取信息
        s = self.redis.get(self.key)
        if s is None:
            self.shopping_cart = []
        else:
            self.shopping_cart = json.loads(s)

    def set_key_value(self, value):
        self.redis.set(self.key, json.dumps(value))
        self.redis.expire(self.key,  self.key_expire_time)

    def add_to_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["number"] += num
                item["last_update_time"] = time.time()
                self.set_key_value(self.shopping_cart)
                return

        self.shopping_cart.append({"product_id": product_id, "number": num, "last_update_time": time.time()})
        self.set_key_value(self.shopping_cart)

    def del_from_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["number"] -= num
                if item["number"] <= 0:
                    self.shopping_cart = [item for item in self.shopping_cart if item["product_id"] != product_id]
                break
        self.set_key_value(self.shopping_cart)
        
    def empty(self):
        self.set_key_value([])

    def data(self, shop_id):
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
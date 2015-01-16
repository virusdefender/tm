# coding=utf-8
import redis
import json
import time

from .models import Product, Shop


class ShoppingCart(object):
    def __init__(self, shopping_cart_key):
        self.key = shopping_cart_key
        # todo
        self.redis = redis.Redis()
        self.shopping_cart = self._shopping_cart()
        # 过期时间 30天
        self.key_expire_time = 60 * 60 * 24 * 30

    def set_key(self, value):
        self.redis.set(self.key, json.dumps(value))
        self.redis.expire(self.key,  self.key_expire_time)

    def _shopping_cart(self):
        shopping_cart = self.redis.get(self.key)
        if shopping_cart is None:
            return []
        else:
            return json.loads(shopping_cart)

    def add_to_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["num"] += num
                item["last_update_time"] = time.time()
                self.set_key(self.shopping_cart)
                return

        self.shopping_cart.append({"product_id": product_id, "num": num, "last_update_time": time.time()})
        self.set_key(self.shopping_cart)

    def del_from_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["num"] -= num
                if item["num"] == 0:
                    self.shopping_cart = [item for item in self.shopping_cart if item["product_id"] != product_id]
                break
        self.set_key(self.shopping_cart)

    def get_product_cart_num(self, product_list):
        response = {}
        for item in product_list:
            flag = 0
            for i in self.shopping_cart:
                if i["product_id"] == item:
                    response[item] = i["num"]
                    flag = 1
                    break
            if not flag:
                response[item] = 0
        return response

    @property
    def shopping_cart_data(self):
        pass
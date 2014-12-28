# coding=utf-8
from .models import Product, Shop


class ShoppingCart(object):
    def __init__(self, request):
        self.shopping_cart = request.session.get("shopping_cart", [])
        self.user = request.user
        # todo
        self.shop = 1

    def add_to_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["num"] += num
                return self.shopping_cart
        self.shopping_cart.append({"product_id": product_id, "num": num})
        return self.shopping_cart

    def del_from_cart(self, product_id, num=1):
        for item in self.shopping_cart:
            if item["product_id"] == product_id:
                item["num"] -= num
                if item["num"] == 0:
                    self.shopping_cart = [item for item in self.shopping_cart if item["product_id"] != product_id]
                break
        return self.shopping_cart

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
        print response
        return response

    @property
    def shopping_cart_data(self):
        data = []
        for item in self.shopping_cart:
            # todo check
            try:
                p = Product.objects.get(shop=self.shop, pk=item["product_id"])
            except Product.DoesNotExist:
                continue
            setattr(p, "_cart_num", item["num"])
            data.append(p)
        return data
# coding=utf-8
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.shortcuts import http_400_response
from .models import Shop, Category, Product
from .serializers import CategorySerializer, ShopSerializer, ProductSerializer, ShoppingCartOperationSerializer
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
        shopping_cart_id = request.session.get("shopping_cart_id", None)
        if not shopping_cart_id:
            return Response(data=[])
        else:
            shopping_cart = ShoppingCart(request.session["shopping_cart_id"])

        try:
            shop_id = int(request.GET.get("shop_id", -1))
        except Exception as e:
            return http_400_response(e)

        data = []
        for item in shopping_cart.data(shop_id):
            data.append({"product": ProductSerializer(item["product"]).data, "number": item["number"]})
        return Response(data=data)

    def post(self, request):
        shopping_cart_id = request.session.get("shopping_cart_id", None)
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

            return Response(data=request.DATA)
        else:
            return http_400_response(serializer.errors)
# coding=utf-8
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.shortcuts import http_400_response
from .models import Shop, Category
from .serializers import CategorySerializer


class CategoryView(APIView):
    def get(self, request):
        shop_id = request.GET.get("shop_id", -1)
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            return http_400_response("Shop does not exist")
        return Response(data=CategorySerializer(Category.objects.filter(shop=shop, parent_category__isnull=True), many=True).data)
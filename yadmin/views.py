# coding=utf-8
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView

from utils.shortcuts import http_400_response, paginate
from shop.models import Order
from shop.serializers import OrderSerializer


class CourierOrderListApiView(APIView):
    def get(self, request):
        if not request.user.is_authenticated() and request.user.is_staff:
            return http_400_response("Login required")
        order_list = Order.objects.filter(courier__user=request.user, order_status__in=[-1, 0, 1]).\
            filter(Q(Q(pay_method="alipay") & Q(payment_status=1)) | Q(Q(pay_method="COD") & Q(payment_status__in=[0, 1]))).order_by("address_category__index")
        return Response(data=OrderSerializer(order_list, many=True).data)

# coding=utf-8
from django.contrib.auth.models import AnonymousUser

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProductDetailClickLog


class LogView(APIView):
    def post(self, request):
        data = request.DATA
        log_type = data.get("log_type", None)
        if log_type == "show_product_detail":
            log_data = {}
            log_data["product_id"] = data.get("product_id", -1)

            if isinstance(request.user, AnonymousUser):
                log_data["session_id"] = request.session._session_key
            else:
                log_data["user"] = request.user
            ProductDetailClickLog.objects.create(**log_data)
        return Response(data="")

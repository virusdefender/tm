# coding=utf-8
import datetime
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from utils.shortcuts import http_400_response

from .models import SignUpLog
from .serializers import SignUpLogSerializer


class SignUpAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated():
            return http_400_response("Login required")
        log = SignUpLog.objects.filter(user=request.user,
                                       create_time__range=(datetime.datetime.now().replace(hour=0, minute=0, second=0),
                                                           datetime.datetime.now()))
        if not log.exists():
            log = SignUpLog.objects.create(user=request.user, score=5, rank=1)
            return Response(data=SignUpLogSerializer(log).data)
        else:
            return Response(data=SignUpLogSerializer(log[0]).data)

    def get(self, request):
        if not request.user.is_authenticated():
            return http_400_response("Login required")
        log = SignUpLog.objects.filter(user=request.user,
                                       create_time__range=(datetime.datetime.now().replace(hour=0, minute=0, second=0),
                                                           datetime.datetime.now()))
        if not log.exists():
            return Response(data={"status": False})

        return Response(data={"status": True, "info": SignUpLogSerializer(log[0]).data})
# coding=utf-8
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView


class AppUpdateAPIView(APIView):
    def get(self, request):
        # status含义 0 不需要升级 1需要升级
        app_version = request.META.get("HTTP_APPVERSION", None)
        if not app_version:
            return Response(data={"status": -1})

        try:
            version = app_version.split("?")[1]
        except Exception:
            return Response(data={"status": -1})

        if version == "1.0":
            return Response(data={"status": 1,
                                  "title": u"版本更新，修复大量bug",
                                  "content": u"1.性能优化\n2.更方便使用 简化操作\n3.xxxxxxxxxxxxxxxxxxxxxx900000123456！@#￥",
                                  "download_url": "http://files.cdn.kechenggezi.com/app/kecheng.apk"})
        else:
            return Response(data={"status": 0})
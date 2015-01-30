# coding=utf-8
import time
import datetime
from decimal import Decimal

from pytz import utc
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, InvalidPage
from rest_framework.response import Response
from rest_framework import pagination
from rest_framework import status


def http_201_response(data):
    return Response(data=data, status=status.HTTP_201_CREATED)


def http_400_response(error_reason, show=0):
    return Response(data={"status": "error", "show": show, "content": error_reason},
                    status=status.HTTP_400_BAD_REQUEST)


def decimal_round(decimal_number):
    split_str = str(decimal_number).split(".")
    if len(split_str) <= 1:
        return decimal_number
    else:
        if len(split_str[1]) > 2:
            return Decimal(split_str[0] + "." + split_str[1][0:2])
        else:
            return decimal_number


def paginate(request, query_set, object_serializer, pagination_serializer=None):
    """
    用于分页的函数
    :param object_serializer: 序列化单个object的serializer 一般只传递这一个就行 自动生成分页的类
    :param pagination_serializer: 如果这个不为None 将使用这个类作为分页工具
    :return:Response
    """
    need_paginate = request.GET.get("paging", None)
    # 如果请求的参数里面没有paging=true的话 就返回全部参数
    if need_paginate != "true":
        return Response(data=object_serializer(query_set, many=True).data)
    page_size = request.GET.get("limit", None)
    if not page_size:
        return http_400_response("Parameter limit is required")
    try:
        page_size = int(page_size)
        if page_size < 1:
            return http_400_response("Invalid limit parameter")
    except (ValueError, TypeError):
        return http_400_response("Invalid limit parameter")

    paginator = Paginator(query_set, page_size)
    page = request.GET.get("page", None)

    try:
        page_data = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        return http_400_response("Invalid page parameter")
    if pagination_serializer:
        serializer = pagination_serializer(page_data, context={"request": request})
        return Response(data=serializer.data)
    else:
        # 动态定义这样一个类
        class PaginationSerializer(pagination.PaginationSerializer):
            class Meta:
                object_serializer_class = object_serializer

        serializer = PaginationSerializer(page_data, context={"request": request})
        return Response(data=serializer.data)
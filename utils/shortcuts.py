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
# coding=utf-8
import time
import datetime

from pytz import utc
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, InvalidPage
from rest_framework.response import Response
from rest_framework import pagination
from rest_framework import status


def http_201_response(data):
    return Response(data=data, status=status.HTTP_201_CREATED)


def http_400_response(error_reason):
    return Response(data={"status": "error", "content": error_reason},
                    status=status.HTTP_400_BAD_REQUEST)
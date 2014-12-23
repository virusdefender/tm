# coding=utf-8
from django.conf.urls import *


from .views import ShopView


urlpatterns = patterns('',
                       url(r"^(?P<shop_id>\d+)/$", ShopView.as_view()),

                       )
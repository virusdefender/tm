from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

from django.contrib import admin
from django.views.generic import TemplateView
from account.views import UserLoginView, UserRegisterView, CaptchaView, UserView, UserLoginPageView
from log.views import LogView
from shop.views import (CategoryAPIView, ShopAPIView, ProductAPIView, ShoppingCartAPIView,
                        ShopIndexPageView, ShoppingCartPageView, SubmitOrderPageView,
                        PayResultPageView, OrderAPIView)

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', TemplateView.as_view(template_name='shop/index.html')),
                       url(r"^captcha/$", CaptchaView.as_view()),
                       url(r"^shop/(?P<shop_id>\d+)/$", ShopIndexPageView.as_view()),
                       url(r"^shopping_cart/$", ShoppingCartPageView.as_view()),
                       url(r"^order/$", SubmitOrderPageView.as_view()),

                       url(r"^pay/(?P<result>\w+)/", PayResultPageView.as_view()),

                       url(r'xadmin/', include(xadmin.site.urls)),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),

                       url(r"^login/$", UserLoginPageView.as_view()),

                       url(r"^api/v1/login/$", UserLoginView.as_view()),
                       url(r"^api/v1/user/$", UserView.as_view()),

                       url(r"^api/v1/captcha/$", CaptchaView.as_view()),
                       url(r"^api/v1/category/$", CategoryAPIView.as_view()),
                       url(r"^api/v1/shop/$", ShopAPIView.as_view()),
                       url(r"^api/v1/product/$", ProductAPIView.as_view()),
                       url(r"^api/v1/shopping_cart/$", ShoppingCartAPIView.as_view()),
                       url(r"^api/v1/order/$", OrderAPIView.as_view()),

)

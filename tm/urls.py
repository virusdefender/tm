from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

from django.contrib import admin
from django.views.generic import TemplateView
from account.views import UserLoginView, UserRegisterView, CaptchaView, UserView
from log.views import LogView
from shop.views import (CategoryView, ShopView, ProductView, ShoppingCartView,
                        ShopIndexView, ShoppingCartIndexView, OrderIndexView, PayResultView)

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', TemplateView.as_view(template_name='shop/index.html')),
                       url(r"^shop/(?P<shop_id>\d+)/$", ShopIndexView.as_view()),
                       url(r"^shopping_cart/$", ShoppingCartIndexView.as_view()),
                       url(r"^order/$", OrderIndexView.as_view()),

                       url(r"^pay/(?P<result>\w+)/", PayResultView.as_view()),

                       url(r'xadmin/', include(xadmin.site.urls)),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),

                       url(r"^api/v1/category/$", CategoryView.as_view()),
                       url(r"^api/v1/shop/$", ShopView.as_view()),
                       url(r"^api/v1/product/$", ProductView.as_view()),
                       url(r"^api/v1/shopping_cart/$", ShoppingCartView.as_view()),

)

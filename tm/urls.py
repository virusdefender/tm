from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

from django.contrib import admin
from django.views.generic import TemplateView
from account.views import (UserLoginAPIView, UserRegisterAPIView, CaptchaView,
                           UserView, UserLoginPageView, UserRegisterPageView,
                           UserChangePasswordPageView, UserResetPasswordPageView,
                           UserResetPasswordSMSAPIView, UserResetPasswordAPIView,
                           UserCenterPageView)
from log.views import LogView
from shop.views import (CategoryAPIView, ShopAPIView, ProductAPIView, ShoppingCartAPIView,
                        ShopIndexPageView, ShoppingCartPageView, SubmitOrderPageView,
                        PayResultPageView, OrderAPIView, OrderListPageView, OrderRepayAPIView,
                        PayNotifyAPIView, AllocateOrderCourierView)
from app.views import AppUpdateAPIView, CSRFTokenAPIView
from signup.views import SignUpAPIView
from yadmin.views import CourierOrderListApiView


admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', TemplateView.as_view(template_name='shop/index.html')),
                       url(r"^captcha/$", CaptchaView.as_view()),
                       url(r"^shop/(?P<shop_id>\d+)/$", ShopIndexPageView.as_view()),
                       url(r"^shopping_cart/$", ShoppingCartPageView.as_view()),
                       url(r"^order/$", SubmitOrderPageView.as_view()),

                       url(r"^my_order/$", OrderListPageView.as_view()),

                       url(r"^pay/notify/$", PayNotifyAPIView.as_view()),

                       url(r"^pay/(?P<result>\w+)/", PayResultPageView.as_view()),

                       url(r'xadmin/', include(xadmin.site.urls)),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),

                       url(r"^user_center/$", UserCenterPageView.as_view()),

                       url(r"^login/$", UserLoginPageView.as_view()),
                       url(r"^register/$", UserRegisterPageView.as_view()),
                       url(r"^reset_password/$", UserResetPasswordPageView.as_view()),
                       url(r"^change_password/$", UserChangePasswordPageView.as_view()),

                       url(r"^api/v1/login/$", UserLoginAPIView.as_view()),
                       url(r"^api/v1/register/$", UserRegisterAPIView.as_view()),
                       url(r"^api/v1/user/$", UserView.as_view()),

                       url(r"^api/v1/reset_password/sms/$", UserResetPasswordSMSAPIView.as_view()),
                       url(r"^api/v1/reset_password/$", UserResetPasswordAPIView.as_view()),

                       url(r"^api/v1/captcha/$", CaptchaView.as_view()),
                       url(r"^api/v1/category/$", CategoryAPIView.as_view()),
                       url(r"^api/v1/shop/$", ShopAPIView.as_view()),
                       url(r"^api/v1/product/$", ProductAPIView.as_view()),
                       url(r"^api/v1/shopping_cart/$", ShoppingCartAPIView.as_view()),
                       url(r"^api/v1/order/$", OrderAPIView.as_view()),
                       url(r"^api/v1/order/repay/$", OrderRepayAPIView.as_view()),

                       url(r"^api/v1/app/update/$", AppUpdateAPIView.as_view()),
                       url(r"^api/v1/app/token/$", CSRFTokenAPIView.as_view()),

                       url(r"^api/v1/signup/$", SignUpAPIView.as_view()),

                       url(r"^allocate/$", AllocateOrderCourierView.as_view()),

                       url(r"^api/v1/yadmin/list/$", CourierOrderListApiView.as_view()),

)

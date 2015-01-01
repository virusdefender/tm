from django.conf.urls import patterns, include, url

from django.contrib import admin
from account.views import UserLoginView, UserRegisterView, CaptchaView, UserView
from shop.views import CategoryView, ProductView, ShoppingCartView, OrderView, PayView
from log.views import LogView

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'tm.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r"^login/$", UserLoginView.as_view()),
                       url(r"^register/$", UserRegisterView.as_view()),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),

                       url(r"^shop/", include("shop.urls")),
                       url(r"^category/$", CategoryView.as_view()),
                       url(r"^product/$", ProductView.as_view()),
                       url(r"^shopping_cart/$", ShoppingCartView.as_view()),
                       url(r"^order/$", OrderView.as_view()),
                       url(r"^log/$", LogView.as_view()),
                       url(r"^captcha/$", CaptchaView.as_view()),
                       url(r'^pay/$', PayView.as_view()),
                       url(r"^user/$", UserView.as_view()),
)

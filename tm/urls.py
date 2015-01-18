from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

from django.contrib import admin
from account.views import UserLoginView, UserRegisterView, CaptchaView, UserView
from log.views import LogView
from shop.views import CategoryView

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'xadmin/', include(xadmin.site.urls)),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),

                       url("^api/v1/category/$", CategoryView.as_view()),
)

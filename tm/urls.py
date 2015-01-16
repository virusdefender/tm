from django.conf.urls import patterns, include, url

import xadmin
xadmin.autodiscover()

from django.contrib import admin
from account.views import UserLoginView, UserRegisterView, CaptchaView, UserView
from log.views import LogView

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'xadmin/', include(xadmin.site.urls)),

                       url(r'^ueditor/', include('DjangoUeditor.urls')),
)

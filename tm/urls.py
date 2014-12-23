from django.conf.urls import patterns, include, url

from django.contrib import admin
from account.views import UserLoginView, UserRegisterView

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'tm.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r"^login/$", UserLoginView.as_view()),
                       url(r"^register/$", UserRegisterView.as_view()),
)

#coding=utf-8
from django.conf.urls import *


urlpatterns = patterns('',
    url(r'^index/$', "utils.ueditor.ueditor", name="editor"),
    url(r'^config/$', "utils.ueditor.ueditor_config", name="editor_config"),
)
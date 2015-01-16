# coding=utf-8
import xadmin
from xadmin import views

from DjangoUeditor.adminx import UEditorWidget

from .models import Shop, OrderLog, Order, OrderProduct, Category, Product


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class ProductAdmin(object):
    style_fields = {"introduction": "ueditor"}
    list_display = ["name", "price"]
    list_editable = ["price", "name", "status"]


class ShopAdmin(object):
    list_display = ["name"]


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(Shop)
xadmin.site.register(Order)
xadmin.site.register(OrderLog)
xadmin.site.register(OrderProduct)
xadmin.site.register(Category)
xadmin.site.register(Product, ProductAdmin)
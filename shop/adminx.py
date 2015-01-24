# coding=utf-8
import xadmin
from xadmin import views
from xadmin.plugins.actions import BaseActionView

from django.http import HttpResponse, HttpResponseRedirect

from .models import Shop, OrderLog, Order, OrderProduct, Category, Product


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class ProductDownAction(BaseActionView):
    action_name = u"product_down_action"
    description = u"下架商品"
    model_perm = "change"

    def do_action(self, query_set):
        query_set.update(status=False)
        return HttpResponseRedirect("/xadmin/shop/product/")


class ProductUpAction(BaseActionView):
    action_name = u"product_up_action"
    description = u"上架商品"
    model_perm = "change"

    def do_action(self, query_set):
        query_set.update(status=True)
        return HttpResponseRedirect("/xadmin/shop/product/")


class ProductAdmin(object):
    style_fields = {"introduction": "ueditor"}
    list_display = ["shop", "category", "name", "price", "status"]
    list_editable = ["price", "name", "status"]
    search_fields = ["name"]
    list_filter = ["status", "category"]
    actions = [ProductDownAction, ProductUpAction]


class ShopAdmin(object):
    list_display = ["name"]

class OrderAdmin(object):
    list_display = ["name", "phone", "pay_method", "payment_status", "order_status", "create_time"]


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(Shop)
xadmin.site.register(Order, OrderAdmin)
xadmin.site.register(OrderLog)
xadmin.site.register(OrderProduct)
xadmin.site.register(Category)
xadmin.site.register(Product, ProductAdmin)
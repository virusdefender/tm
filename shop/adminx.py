# coding=utf-8
import json
import xadmin
from xadmin import views
from xadmin.plugins.actions import BaseActionView

from django.http import HttpResponse, HttpResponseRedirect

from .models import Shop, OrderLog, Order, OrderProduct, Category, Product, Courier, AddressCategory


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


class AllocateCourierAction(BaseActionView):
    action_name = u"allocate_courire_action"
    description = u"分配送货人员"
    model_perm = "change"

    def do_action(self, query_set):
        l = [item.id for item in query_set]
        return HttpResponseRedirect("/allocate/?l=" + json.dumps(l))


class OrderAdmin(object):
    list_display = ["user", "name", "phone", "total_price", "pay_method", "payment_status", "order_status", "create_time", "courier", "address_category"]
    list_filter = ["pay_method", "payment_status", "order_status", "create_time", "courier"]
    list_editable = ["order_status", "address_category"]
    show_detail_fields = ["user"]
    list_display_links = ["user"]
    actions = [AllocateCourierAction]


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(Shop)
xadmin.site.register(Order, OrderAdmin)
xadmin.site.register(OrderLog)
xadmin.site.register(OrderProduct)
xadmin.site.register(Category)
xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(Courier)
xadmin.site.register(AddressCategory)
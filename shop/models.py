# coding=utf-8
import time
import datetime
from decimal import Decimal

from django.db import models

from DjangoUeditor.models import UEditorField


class Shop(models.Model):
    """商店"""
    name = models.CharField(max_length=50, db_index=True, help_text=u"商店的名字")
    logo = models.CharField(max_length=200, blank=True, null=True, help_text=u"logo地址")
    delivery_time = models.CharField(max_length=200, help_text=u"送货时间，请严格遵循标准，例子: 10:05-13:00;15:00-19:00")
    contact_information = models.CharField(max_length=200, help_text=u"联系信息，会在订单页面显示")
    delivery_area = models.CharField(max_length=200, blank=True, help_text=u"配送区域")
    create_time = models.DateTimeField(auto_now_add=True)
    admin = models.ManyToManyField("account.User", blank=True, null=True)
    # signup_score = models.IntegerField(help_text=u"一次签到的积分数目")
    status = models.BooleanField(default=True, help_text=u"如果设置为false，代表关闭商店")
    freight_line = models.DecimalField(help_text=u"低于这个价格将收取运费", max_digits=10, decimal_places=2)
    freight = models.DecimalField(help_text=u"运费", max_digits=10, decimal_places=2)
    banner = models.TextField(help_text=u"商店上部轮播广告", blank=True, null=True)

    class Meta:
        db_table = "shop"

    def __unicode__(self):
        return "%s" % self.name

    def get_delivery_time(self):
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        delivery_time_list = []
        time_list = self.delivery_time.split(";")

        for item in time_list:
            start_hour = time.strptime(item.split("-")[0], "%H:%M").tm_hour
            start_min = time.strptime(item.split("-")[0], "%H:%M").tm_min
            end_hour = time.strptime(item.split("-")[1], "%H:%M").tm_hour
            end_min = time.strptime(item.split("-")[1], "%H:%M").tm_min

            now_min = hour * 60 + minute
            d_time = start_hour * 60 + start_min

            if d_time >= now_min and d_time <= end_hour * 60 + end_min:
                delivery_time_list.append(item)
        if not delivery_time_list:
            delivery_time_list = [unicode(item) + u"(第二天)" for item in time_list]

        return delivery_time_list


SORT_TYPE_CHOICES = (("-create_time", u"按照发布时间正向排序"),
                     ("create_time", u"按照发布时间逆向排序"),
                     ("-bought_num", u"按照销量正向排序"),
                     ("bought_num", u"按照销量逆向排序"),
                     ("custom_sort", u"自定义排序"))


class Category(models.Model):
    """商品分类"""
    shop = models.ForeignKey(Shop, help_text=u"这个分类属于哪个商店")
    name = models.CharField(max_length=50, db_index=True, help_text=u"分类的名字")
    sort_type = models.CharField(max_length=20, choices=SORT_TYPE_CHOICES, default="-create_time",
                                 help_text=u"注意，排序方法只需要设置在二级分类，一级分类无效")
    sort_index = models.IntegerField(help_text=u"分类排序，注意二级分类同一个父分类下不要有重复的，一级分类同一个商店内不要有重复的")
    parent_category = models.ForeignKey("self", related_name="child_category",
                                        blank=True, null=True, help_text=u"指向父级分类")

    class Meta:
        db_table = "category"

    def __unicode__(self):
        return "%s %s" % (self.name, self.shop.name)

    def get_category_product(self):
        # 是二级分类
        if self.parent_category:
            if self.sort_type != "custom_sort":
                return Product.objects.filter(category=self).order_by(self.sort_type)
            else:
                return Product.objects.filter(category=self).order_by("-sort_index")
        # 是一级分类
        else:
            product_list = []

            for item in Category.objects.filter(parent_category=self).order_by("-sort_index"):
                if self.sort_type != "custom_sort":
                    for p in Product.objects.filter(category=item).order_by(self.sort_type):
                        product_list.append(p)
                else:
                    for p in Product.objects.filter(category=item).order_by("-sort_index"):
                        product_list.append(p)
            return product_list


class Product(models.Model):
    """一个商品的表"""
    shop = models.ForeignKey(Shop, help_text=u"这个商品是哪个商店的")
    category = models.ForeignKey(Category, help_text=u"这个商品属于哪个分类的")
    name = models.CharField(max_length=50, help_text=u"商品名称")
    # 现在在首页上 标题下面的 可能还会修改
    simple_introduction = models.CharField(max_length=200, help_text=u"显示在商品名称下面的简介")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text=u"售价")
    # 原价 用来计算利润用的
    origin_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, help_text=u"进价，用来计算利润用的")
    # 单位 比如斤/5个 等等
    unit = models.CharField(max_length=50, help_text=u"单位")
    # 首页小图
    preview_pic = models.CharField(max_length=500, help_text=u"图片小图")
    total_num = models.IntegerField(default=10000, help_text=u"库存数量")
    sold_num = models.IntegerField(default=0, help_text=u"该商品已经售出数量")
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify_time = models.DateTimeField(auto_now=True)
    introduction = UEditorField(help_text=u"点击商品弹框显示内容")
    # False的话是商品下架 不会再显示 不要删除商品 因为很多历史订单会用到的
    status = models.BooleanField(default=True, help_text=u"false就是商品下架")
    sort_index = models.IntegerField(help_text=u"排序，注意同一个二级分类下不要有重复的")

    class Meta:
        db_table = "product"
        unique_together = ["category", "sort_index"]

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.shop.name, self.price)

    def create_order_product(self, order, number):
        OrderProduct.objects.create(order=order, number=number, preview_pic=self.preview_pic,
                                    price=self.price, origin_price=self.origin_price, unit=self.unit)


class AddressCategory(models.Model):
    name = models.CharField(max_length=30)
    keywords = models.TextField(help_text=u"请务必使用英文分号分隔关键词，比如汇园;汇一，最后不要加分号")
    shop = models.ForeignKey(Shop)
    index = models.IntegerField(default=0, help_text=u"送货顺序")

    class Meta:
        db_table = "address_category"


class Order(models.Model):
    user = models.ForeignKey("account.User")
    shop = models.ForeignKey(Shop)
    # 支付方式 支付宝或者货到付款
    pay_method = models.CharField(max_length=20, choices=(("alipay", u" 支付宝"), ("COD", "货到付款")))
    alipay_order_id = models.CharField(max_length=50, blank=True, null=True)
    # 支付状态 0 没有付款 -1 已经退款 1 支付成功
    payment_status = models.IntegerField(default=0, choices=((0, u"没有付款"), (-1, u"已经退款"), (1, u" 支付成功")))
    alipay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    # 订单配送状态：等待处理-1  已经确认0  正在配送1  订单完成 2  订单取消 3
    order_status = models.IntegerField(default=-1, choices=((-1, u"等待处理"), (0, u"已经确认"),
                                                            (1, u"正在配送"), (2, u" 订单完成"),
                                                            (3, u"订单取消")))
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=100)
    address_category = models.ForeignKey(AddressCategory, blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    is_first = models.BooleanField(default=False)

    class Meta:
        db_table = "shop_order"

    def __unicode__(self):
        return "%s %s" % (self.name, self.phone)


class OrderProduct(models.Model):
    """类似商品快照 有一个字段和商品关联 还保存了关键信息
    """
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=50)
    preview_pic = models.CharField(max_length=2500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    origin_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    number = models.IntegerField()

    class Meta:
        db_table = "order_product"

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.price, self.origin_price)

    @property
    def total_money(self):
        pass

    @property
    def profit(self):
        pass


class OrderLog(models.Model):
    order = models.ForeignKey(Order)
    content = models.CharField(max_length=200)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_log"

    def __unicode__(self):
        return "%s" % self.content

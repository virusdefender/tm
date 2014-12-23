# coding=utf-8
import time
import json
import datetime
from django.db import models

from DjangoUeditor.models import UEditorField


class Shop(models.Model):
    """商店"""
    name = models.CharField(max_length=50, db_index=True, help_text=u"商店的名字")
    delivery_time = models.CharField(max_length=200, help_text=u"送货时间，请严格遵循标准，例子: 10:05-13:00;15:00-19:00")
    contact_information = models.CharField(max_length=200, help_text=u"联系信息，会在订单页面显示，可以为html")
    # 首单起运价格
    first_order_min_money = models.DecimalField(max_digits=10, decimal_places=2, help_text=u"首单起运价格")
    # 正常起运限制价格
    ordinary_min_money = models.DecimalField(max_digits=10, decimal_places=3, help_text=u"正常起运价格")
    delivery_area = models.CharField(max_length=200, blank=True, help_text=u"配送区域")
    create_time = models.DateTimeField(auto_now_add=True)
    delivery_prepare_time = models.IntegerField(default=0, help_text=u"配送准备时间，系统提前这个时间结束下个时间段的预定，单位分钟")
    # 超级管理员 可以管理下面的admin
    # shop_super_admin = models.ForeignKey("account.User", related_name="super_admin", help_text=u"超级管理员")
    # 普通管理员
    # admin = models.ManyToManyField("account.User", blank=True, null=True,
    # related_name="shop_admin", help_text=u"普通管理员，暂时没用到")
    announcement = models.TextField(blank=True, null=True, help_text=u"全局公告")
    personalized_recommendation = models.BooleanField(default=True, help_text=u"是否开启个性化推荐")
    status = models.BooleanField(default=True, help_text=u"如果设置为false，代表关闭商店")

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

            if d_time - now_min >= self.delivery_prepare_time and d_time <= end_hour * 60 + end_min:
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
    is_index = models.BooleanField(default=False, help_text=u"如果为true，打开商店首页显示的将是这个分类")
    sort_index = models.IntegerField(default=0, help_text=u"商店首页顶部分类名称排序")
    parent_category = models.ForeignKey("self", related_name="child_category", blank=True, null=True, help_text=u"指向父级分类")

    class Meta:
        db_table = "category"

    def __unicode__(self):
        return "%s %s" % (self.name, self.shop.name)


class Icon(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=200)

    class Meta:
        db_table = "icon"

    def __unicode__(self):
        return self.name


class UserGroup(models.Model):
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_group"


class Product(models.Model):
    """一个商品的表"""
    shop = models.ForeignKey(Shop, help_text=u"这个商品是哪个商店的")
    category = models.ForeignKey(Category, help_text=u"这个商品属于哪个分类的")
    name = models.CharField(max_length=50, help_text=u"商品名称,如果是多个口味的，这里不要填写口味。")
    icons = models.ManyToManyField(Icon, blank=True, null=True, help_text=u"商品小图标")
    # remark是商品的附加说明字段 比如商品名称是西瓜 你可以在备注中写赠送勺子 然后打印订单的时候会显示备注的
    remark = models.CharField(max_length=50, blank=True, help_text=u"备注，打印订单的时候会显示在商品名称最后面")
    # 现在在首页上 标题下面的 可能还会修改
    simple_introduction_top = models.CharField(max_length=200, default='<span style="color:red">￥元/袋</span>', help_text=u"显示在商品名称下面的简介")
    simple_introduction_foot = models.CharField(max_length=200, blank=True, help_text=u"显示在上面那个简介下面的简介，暂时没显示")
    price = models.DecimalField(max_digits=10, decimal_places=3, help_text=u"售价")
    # 原价 用来计算利润用的
    origin_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, help_text=u"进价，用来计算利润用的")
    # 单位 比如斤/5个 等等
    unit = models.CharField(max_length=50, help_text=u"单位")
    # 最多购买数量 -1表示无限制 ;0表示这个物品只能展示 不能购买 ;>0的正常限制
    max_num = models.IntegerField(default=-1, help_text=u"最多购买数量 -1表示无限制 ;0表示这个物品只能展示 不能购买 >0的正常限制")
    # 首页小图
    preview_pic = models.CharField(max_length=200, help_text=u"图片小图")
    total_num = models.IntegerField(default=10000, help_text=u"库存数量")
    bought_num = models.IntegerField(default=0, help_text=u"该商品已经售出数量")
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify_time = models.DateTimeField(auto_now=True)
    introduction = UEditorField(help_text=u"点击商品弹框显示内容")
    min_score = models.IntegerField(default=0, help_text=u"最低积分")
    # False的话是商品下架 不会再显示 不要删除商品 因为很多历史订单会用到的
    status = models.BooleanField(default=True, help_text=u"false就是商品下架")
    sort_index = models.IntegerField(default=0, help_text=u"商品排序索引")
    # 如果为True 说明为虚拟商品，分类用的，不能购买
    is_virtual = models.BooleanField(default=False, help_text=u"如果为True 说明为虚拟商品，分类用的，不能购买")
    # 如果这是不同口味的，就指向父商品
    parent_product = models.ForeignKey("self", blank=True, null=True, help_text=u"如果这是不同口味的，就指向父商品")
    # 口味的名字
    attr = models.CharField(max_length=20, blank=True, null=True, help_text=u"口味，颜色等属性")
    user_group = models.ManyToManyField(UserGroup, blank=True, null=True, help_text=u"只有属于这个分组里面的才能购买")

    class Meta:
        db_table = "product"

    def __unicode__(self):
        return "%s %s %s %s" % (self.name, self.shop.name, self.price, self.is_virtual)

    def create_order_product(self, order, number):
        if self.parent_product and self.is_virtual is False:
            name = self.name + self.attr
        else:
            name = self.name
        # 更新已购数目 注意虚拟商品
        if self.parent_product:
            self.parent_product.bought_num += number
            self.parent_product.save()
        else:
            self.bought_num += number
            self.save()
        order_product = OrderProduct.objects.create(name=name,
                                                    order=order,
                                                    remark=self.remark,
                                                    preview_pic=self.preview_pic,
                                                    price=self.price,
                                                    origin_price=self.origin_price,
                                                    unit=self.unit, number=number)
        return order_product


class Order(models.Model):
    user = models.ForeignKey("account.User")
    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=100)
    remark = models.CharField(max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.CharField(max_length=200)
    # status 可能有下面几种 等待处理 0 已经发货  1 订单完成 2 订单取消 3
    status = models.IntegerField(default=0)
    source = models.CharField(max_length=20, default="web")
    total_money = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    is_first = models.BooleanField(default=False)

    class Meta:
        db_table = "order"

    def add_order_product(self, product_id, number):
        product = Product.objects.get(pk=product_id)
        product.save()
        product.create_order_product(self, number)

    def add_log(self, content):
        OrderLog.objects.create(order=self,
                                content=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + content)

    def get_total_money(self):
        order_product = OrderProduct.objects.filter(order=self)
        total_money = 0
        for item in order_product:
            total_money += item.total_money
        return total_money

    def get_profit(self):
        order_product = OrderProduct.objects.filter(order=self)
        profit = 0
        for item in order_product:
            profit += item.profit
        return profit

    def get_delivery_time(self):
        try:
            return json.loads(self.delivery_time)
        except Exception:
            return ["error"]

    def __unicode__(self):
        return "%s %s" % (self.name, self.phone)


class OrderProduct(models.Model):
    """类似商品快照 有一个字段和商品关联 还保存了关键信息
    """
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=50)
    remark = models.CharField(max_length=100, blank=True)
    preview_pic = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    origin_price = models.DecimalField(max_digits=10, decimal_places=3)
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
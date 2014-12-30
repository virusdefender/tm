# coding=utf-8
import time
from django.db import models

from account.models import User


class AbstractLog(models.Model):
    time = models.FloatField(default=time.time)
    # 匿名用户
    session_id = models.CharField(max_length=35, blank=True, null=True)
    # 登陆用户
    user = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        abstract = True


class CategoryClickLog(AbstractLog):
    category_id = models.IntegerField()

    class Meta:
        db_table = "category_click_log"


class ProductDetailClickLog(AbstractLog):
    product_id = models.IntegerField()

    class Meta:
        db_table = "product_detail_click_log"


class ShoppingCartOperationLog(AbstractLog):
    # index / shopping cart
    source = models.CharField(max_length=10)
    # +1 / -1
    operation = models.CharField(max_length=10)
    product_id = models.IntegerField()

    class Meta:
        db_table = "shopping_cart_operation_log"
# coding=utf-8
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from shop.models import (Shop, Location)


class DecoratorTest(TestCase):
    def setUp(self):
        #user1是staff
        self.user1 = User(username="user1")
        self.user1.set_password("111111")
        self.user1.is_staff = True
        self.user1.save()
        #user2是shop1的超级管理员
        self.user2 = User(username="user2")
        self.user2.set_password("111111")
        self.user2.save()
        #user3是首批shop2的超级管理员
        self.user3 = User(username="user3")
        self.user3.set_password("111111")
        self.user3.save()
        self.client = Client()
        self.location = Location.objects.create(location_name=u"qdu center")
        self.shop1 = Shop.objects.create(name="shop1", delivery_time="111", contact_information="111",
                                         location=self.location, shop_super_admin=self.user2)
        self.shop2 = Shop.objects.create(name="shop2", delivery_time="111", contact_information="111",
                                         location=self.location, shop_super_admin=self.user3)

    def test_system_admin_required(self):
        #系统管理员  正常情况
        self.client.login(username="user1", password="111111")
        response = self.client.get(reverse("system_management_index"))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        #非系统管理员
        self.client.login(username="user2", password="111111")
        response = self.client.get(reverse("system_management_index"))
        self.assertEqual(response.status_code, 403)
        #未登录状态
        self.client.logout()
        response = self.client.get(reverse("system_management_index"))
        self.assertEqual(response.status_code, 403)

    def test_shop_super_admin_required(self):
        #user2是商店的超级管理员
        self.client.login(username="user2", password="111111")
        response = self.client.get(reverse("edit_shop", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 200)
        #user2不是这个商店的超级管理员
        response = self.client.get(reverse("edit_shop", kwargs={"shop_id": self.shop2.id}))
        self.assertEqual(response.status_code, 403)
        #user1是超级管理员
        self.client.login(username="user1", password="111111")
        response = self.client.get(reverse("edit_shop", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 200)
        #商店不存在
        response = self.client.get(reverse("edit_shop", kwargs={"shop_id": 222}))
        self.assertEqual(response.status_code, 404)
        #未登录状态
        self.client.logout()
        response = self.client.get(reverse("edit_shop", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 403)

    def test_shop_admin_required(self):
        #系统管理员 正常
        self.client.login(username="user1", password="111111")
        response = self.client.get(reverse("shop_management_index", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        #use2是shop1的超级管理员 正常
        self.client.login(username="user1", password="111111")
        response = self.client.get(reverse("shop_management_index", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        #把user3设置为shop1的普通管理员
        self.shop1.admin.add(self.user3)
        self.shop1.save()
        self.client.login(username="user1", password="111111")
        response = self.client.get(reverse("shop_management_index", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 200)
        #创建普通账户user4
        user4 = User(username='user4')
        user4.set_password("111111")
        self.client.logout()
        self.client.login(username="user4", password="111111")
        response = self.client.get(reverse("shop_management_index", kwargs={"shop_id": self.shop1.id}))
        self.assertEqual(response.status_code, 403)



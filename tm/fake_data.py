# coding=utf-8
import json
import random
from shop.models import Category, Shop, Product
from account.models import User


def create_product(shop, name, category, price, sort_index):
    Product.objects.create(shop=shop, category=category, name=name, price=price,
                           origin_price=1.02, unit=u"个",
                           simple_introduction="x元/份，特惠价",
                           preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                       "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                           total_num=100, sold_num=10,
                           introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                        "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                           sort_index=sort_index)


def create_fake_data():
    u = User.objects.create(username="root")
    u.is_superuser = True
    u.is_staff = True
    u.default_shop_id = 1
    u.set_password("root")
    u.save()

    u1 = User.objects.create(username="test")
    u1.set_password("test")
    u1.save()

    u2 = User.objects.create(username="test2")
    u2.set_password("test2")
    u2.save()

    s1 = Shop.objects.create(name="天目青大店", delivery_time="9:00-10:30;13:00-16:00",
                             contact_information="电话：123456",
                             delivery_area="青岛大学中心校区", freight_line=20, freight=4,
                             banner=json.dumps([
                                 "http://tmimage.b0.upaiyun.com/1421293126%E6%94%BE%E5%81%87%E9%80%9A%E7%9F%A5%E5%89%AF%E6%9C%AC.jpg",
                                 "http://tmimage.b0.upaiyun.com/1421293126%E6%94%BE%E5%81%87%E9%80%9A%E7%9F%A5%E5%89%AF%E6%9C%AC.jpg"
                             ]))

    c1 = Category.objects.create(shop=s1, name=u"测试1", sort_index=1)
    c2 = Category.objects.create(shop=s1, name=u"测试2", sort_index=2)

    c6 = Category.objects.create(shop=s1, name=u"测试3", sort_index=3, parent_category=c1)
    c7 = Category.objects.create(shop=s1, name=u"测试4", sort_index=4, parent_category=c1)
    c8 = Category.objects.create(shop=s1, name=u"测试5", sort_index=5, parent_category=c1)
    c9 = Category.objects.create(shop=s1, name=u"测试6", sort_index=6, parent_category=c1)
    c10 = Category.objects.create(shop=s1, name=u"测试7", sort_index=7, parent_category=c1)

    c11 = Category.objects.create(shop=s1, name=u"测试8", sort_index=3, parent_category=c2)
    c12 = Category.objects.create(shop=s1, name=u"测试9", sort_index=4, parent_category=c2)
    c13 = Category.objects.create(shop=s1, name=u"测试10", sort_index=5, parent_category=c2)
    c14 = Category.objects.create(shop=s1, name=u"测试11", sort_index=6, parent_category=c2)
    c15 = Category.objects.create(shop=s1, name=u"测试12", sort_index=7, parent_category=c2)


    for item in Category.objects.filter(parent_category__isnull=False):
        for i in range(10):
            create_product(shop=s1, category=item, price=random.randint(100, 500) / 100,
                           name=u"唇动牛奶味蛋糕" + str(item.id) + str(i), sort_index=i)
    '''
    p1 = Product.objects.create(shop=s1, category=c6, name=u"唇动牛奶味蛋糕1", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)
    p2 = Product.objects.create(shop=s1, category=c6, name=u"唇动牛奶味蛋糕2", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=2)
    p3 = Product.objects.create(shop=s1, category=c6, name=u"唇动牛奶味蛋糕3", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=3)
    p4 = Product.objects.create(shop=s1, category=c6, name=u"唇动牛奶味蛋糕4", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=4)
    p5 = Product.objects.create(shop=s1, category=c7, name=u"唇动牛奶味蛋糕5", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)
    p5 = Product.objects.create(shop=s1, category=c7, name=u"唇动牛奶味蛋糕6", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=2)
    p7 = Product.objects.create(shop=s1, category=c7, name=u"唇动牛奶味蛋糕7", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=3)
    p8 = Product.objects.create(shop=s1, category=c7, name=u"唇动牛奶味蛋糕8", price=1.2,
                                origin_price=1.02, unit=u"个",
                                simple_introduction="x元/份，特惠价",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, sold_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=4)
    '''


create_fake_data()
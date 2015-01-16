# coding=utf-8
from shop.models import Category, Shop, Product
from account.models import User


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

    s1 = Shop.objects.create(name="test", delivery_time="9:00-10:30;13:00-16:00",
                             contact_information="phone 123456",
                             delivery_area="111", signup_score=5, score_balance_rate=0.01, freight_line=20, freight=4)

    c1 = Category.objects.create(shop=s1, name=u"测试", sort_index=1)
    c2 = Category.objects.create(shop=s1, name=u"测试", sort_index=3)
    c3 = Category.objects.create(shop=s1, name=u"测试", sort_index=2)
    c4 = Category.objects.create(shop=s1, name=u"测试", sort_index=5)
    c5 = Category.objects.create(shop=s1, name=u"测试", sort_index=4)
    c6 = Category.objects.create(shop=s1, name=u"测试", sort_index=-1, parent_category=c1)
    c7 = Category.objects.create(shop=s1, name=u"测试", sort_index=-2, parent_category=c1)
    c8 = Category.objects.create(shop=s1, name=u"测试", sort_index=-4, parent_category=c1)
    c9 = Category.objects.create(shop=s1, name=u"测试", sort_index=-3, parent_category=c1)
    c10 = Category.objects.create(shop=s1, name=u"测试", sort_index=-3, parent_category=c1)

    p1 = Product.objects.create(shop=s1, category=c2, name=u"唇动牛奶味蛋糕1", price=1.2,
                                origin_price=1.02, unit=u"个",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, bought_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)
    p1 = Product.objects.create(shop=s1, category=c3, name=u"唇动牛奶味蛋糕1", price=1.2,
                                origin_price=1.02, unit=u"个",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, bought_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)
    p1 = Product.objects.create(shop=s1, category=c3, name=u"唇动牛奶味蛋糕1", price=1.2,
                                origin_price=1.02, unit=u"个",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, bought_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)
    p1 = Product.objects.create(shop=s1, category=c3, name=u"唇动牛奶味蛋糕1", price=1.2,
                                origin_price=1.02, unit=u"个",
                                preview_pic="https://tmimage.b0.upaiyun.com/1417489338%E6%97%BA%E6%9"
                                            "7%BA%E4%BB%99%E8%B4%9D%E5%B0%8F.jpg",
                                total_num=100, bought_num=10,
                                introduction="<img src='http://tmimage.b0.upaiyun.com/141733908617."
                                             "%E5%94%87%E5%8A%A8%E7%89%9B%E5%A5%B6.png'>",
                                sort_index=1)


create_fake_data()
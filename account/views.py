# coding=utf-8
import json
import requests

import random
import time
from django.db.models import Sum
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from account.models import User, LoginLog, PasswordRecoveryLog
from shop.models import Order


class UserLoginView(APIView):
    def get(self, request):
        return render(request, "account/login.html")

    def post(self, request):
        return Response(data={"status": "error", "content": u"用户名或密码错误"})


class UserRegisterView(APIView):
    def get(self, request):
        return render(request, "account/register.html")

    def post(self, request):
        return Response(data={"status": "error", "content": u"注册失败"})


def get_user_rank(user):
    if not user.is_authenticated():
        return {"rank": 0, "score": -1, "name": u"不是会员", "discount": 1}
    score = user.score
    if score < 50:
        return {"rank": 1, "score": score, "name": u"不是会员", "discount": 1}
    if 50 <= score < 100:
        return {"rank": 2, "score": score, "name": u"初级会员", "discount": 0.99}
    if 100 <= score < 200:
        return {"rank": 3, "score": score, "name": u"中级会员", "discount": 0.98}
    if 200 <= score < 300:
        return {"rank": 4, "score": score, "name": u"高级会员", "discount": 0.97}
    return {"rank": 5, "score": score, "name": u"骨灰级会员", "discount": 0.95}



'''
@login_required(login_url="/login/")
def my_info(request):
    return render(request, "account/my_info.html")


def show_captcha(request):
    captcha = Captcha(request)
    return captcha.display()


def send_sms(username, phone, password):
    accesskey = "2912"
    secretkey = "aee670d7603abee1c37bfda2ca1270fdeea4ff02"
    url = u"""sms.bechtech.cn/Api/send/data/json?accesskey=%s&secretkey=%s&mobile=%s&content=亲爱的%s，您正在申请重置密码，新密码是%s，登陆后请重新设置密码。【天目】""" % (accesskey, secretkey, phone, username, password)
    print url
    try:
        r = requests.get("http://" + url)
        print r.content
    except Exception, e:
        print "send sms failed" + phone + username
        print e


def reset_password(request):
    if request.method == "GET":
        return render(request, "account/reset_password.html")
    else:
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            phone = form.cleaned_data["phone"]
            captcha_code = form.cleaned_data["captcha"]
            captcha = Captcha(request)
            if not captcha.check(captcha_code):
                return HttpResponse(json.dumps({"status": "error", "content": u"验证码错误"}))
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return HttpResponse(json.dumps({"status": "error", "content": u"用户名不存在"}))
            try:
                security = Security.objects.get(user=user)
                if time.time() - security.last_sms_time < 120:
                    return HttpResponse(json.dumps({"status": "error", "content": u"验证码间隔太短"}))
                security.last_sms_time = time.time()
                password = "".join(random.sample('0123456789', 6))
                user.set_password(password)
                user.is_active = True
                user.save()
                send_sms(user.username, user.phone, password)
                return HttpResponse(json.dumps({"status": "success", "redirect": "/login/?next=/change_password/"}))
            except Security.DoesNotExist:
                if phone == user.phone:
                    Security.objects.create(user=user, last_sms_time=time.time())
                    password = "".join(random.sample('0123456789', 6))
                    user.set_password(password)
                    user.save()
                    send_sms(user.username, user.phone, password)
                    return HttpResponse(json.dumps({"status": "success",
                                                    "redirect": "/login/?next=/change_password/&username=" + username}))
                else:
                    return HttpResponse(json.dumps({"status": "error", "content": u"手机号码错误或没有预留手机号码"}))
        else:
            return HttpResponse(json.dumps({"status": "error", "content": u"表单数据错误"}))


@login_required(login_url="/login/")
def change_password(request):
    if request.method == "GET":
        return render(request, "account/change_password.html")
    else:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]
            confirm_old_password = form.cleaned_data["confirm_new_password"]
            if new_password != confirm_old_password:
                return HttpResponse(json.dumps({"status": "error", "content": u"两个密码不一致"}))
            user = auth.authenticate(username=request.user.username, password=old_password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                return HttpResponse(json.dumps({"status": "success", "redirect": "/login/?username=" + user.username}))
            else:
                return HttpResponse(json.dumps({"status": "error", "content": u"老密码错误"}))
        else:
            return HttpResponse(json.dumps({"status": "error", "content": u"表单验证错误"}))


def change_sex(request):
    if request.method == "POST":
        sex = request.POST.get("sex", None)
        if sex in ["m", "f"]:
            user = request.user
            user.sex = sex
            user.save()
            return HttpResponse(json.dumps({"status": "success"}))
    return HttpResponse(json.dumps({"status": "error"}))


@login_required(login_url="/login/")
def user_profile(request, user_id):
    if not request.user.is_staff:
        raise Http404
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404
    order = Order.objects.filter(user=user).order_by("-create_time")
    actual_order = order.filter(~Q(status=3))
    order_number = actual_order.count()
    order_total_money = actual_order.aggregate(Sum('total_money'))["total_money__sum"]
    milk_order = MilkOrder.objects.filter(user=user).order_by("-create_time")
    milk_order_number = milk_order.count()
    if order_total_money == None or order_number == 0:
        order_average_money = 0
    else:
        order_average_money = round(order_total_money / float(order_number), 2)
    sign_up = SignupLog.objects.filter(user=user).order_by("-date")
    sign_up_number = sign_up.count()
    return render(request, "account/user_profile.html", {"user": user,
                                                         "order": order,
                                                         "order_number": order_number,
                                                         "order_total_money": order_total_money,
                                                         "milk_order": milk_order,
                                                         "milk_order_number": milk_order_number,
                                                         "sign_up": sign_up,
                                                         "sign_up_number": sign_up_number,
                                                         "order_average_money": order_average_money})
'''
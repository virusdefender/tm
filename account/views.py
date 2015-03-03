# coding=utf-8
import time
import random
import logging

from django.shortcuts import render
from django.contrib import auth
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect

from DjangoCaptcha import Captcha

from rest_framework.views import APIView
from rest_framework.response import Response

from utils.shortcuts import http_400_response
from utils.sms import send_sms
from shop.models import Order
from .models import User, LoginLog, PasswordRecoverySMSLog
from .serializers import (UserLoginSerializer, UserRegisterSerializer, UserInfoSerializer,
                          UserChangePasswordSerializer, UserResetPasswordSerializer, UserResetPasswordSMSSerializer)


def check_is_need_captcha(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return True
    if user.is_staff or user.is_superuser:
        return True
    return False


class UserLoginPageView(APIView):
    def get(self, request):
        return TemplateResponse(request, "account/login.html")


class UserRegisterPageView(APIView):
    def get(self, request):
        return render(request, "account/register.html")


class UserResetPasswordPageView(APIView):
    def get(self, request):
        return render(request, "account/reset_password.html")


class UserChangePasswordPageView(APIView):
    def get(self, request):
        return render(request, "account/change_password.html")


class UserCenterPageView(APIView):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/")
        return render(request, "account/user_center.html")


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data

            if check_is_need_captcha(data["username"]):
                captcha = Captcha(request)
                if not captcha.check(data["captcha"]):
                    return Response(data={"status": "error", "show": 1, "content": u"验证码错误"})

            user = auth.authenticate(username=data["username"], password=data["password"])

            if user is not None:
                if user.is_active:
                    shopping_cart_id = request.session.get("shopping_cart_id", None)

                    auth.logout(request)
                    auth.login(request, user)
                    if shopping_cart_id:
                        request.session["shopping_cart_id"] = shopping_cart_id

                    return Response(data={"status": "success", "user": UserInfoSerializer(request.user).data})
                else:
                    return Response(data={"status": "error", "show": 1, "content": u"用户状态异常"})
            else:
                try:
                    user = User.objects.get(username=data["username"])
                except User.DoesNotExist:
                    pass
                return Response(data={"status": "error", "show": 1, "content": u"用户名或密码错误"})
        else:
            return Response(data={"status": "error", "show": 1, "content": u"用户名或密码错误"})


class UserRegisterAPIView(APIView):
    def get(self, request):
        return Response(data=random.choice([True, False]))
        #return render(request, "account/register.html")

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            try:
                User.objects.get(username=data["username"])
                return Response(data={"status": "error", "show": 1, "content": u"用户名已经存在"})
            except User.DoesNotExist:
                pass
            if len(data["password"]) < 6:
                return Response(data={"status": "error", "show": 1, "content": u"密码太短"})
            user = User.objects.create(username=data["username"])
            user.set_password(data["password"])
            user.save()

            shopping_cart_id = request.session.get("shopping_cart_id", None)

            auth.logout(request)

            auth_user = auth.authenticate(username=data["username"], password=data["password"])
            auth.login(request, auth_user)
            if shopping_cart_id:
                request.session["shopping_cart_id"] = shopping_cart_id
            return Response(data={"status": "success", "user_info": UserInfoSerializer(user).data}, status=201)
        return Response(data={"status": "error", "show": 1, "content": u"注册失败"})


class UserChangePasswordAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated():
            return http_400_response("Login required", 1)
        serializer = UserChangePasswordSerializer(request.DATA)
        if serializer.is_valid():
            pass
        else:
            return http_400_response(serializer.errors)


class UserResetPasswordSMSAPIView(APIView):
    def post(self, request):
        serializer = UserResetPasswordSMSSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data

            # 判断用户和手机号是否存在 是否超过频率限制等等  假如没问题
            if Order.objects.filter(user__username=data["username"], phone=data["phone"]).exists():
                verify_code = random.randint(100000, 999999)
                # 异步队列
                sms_content = u"亲爱的%s，您正在申请重置密码，验证码是%s，请勿泄露！【天目】" % (data["username"], verify_code)
                send_sms.delay(data["phone"], sms_content)

                PasswordRecoverySMSLog.objects.create(code=verify_code, username=data["username"],
                                                      phone=data["phone"], expires_at=int(time.time()) + 1200)
                return Response(data={"status": "success"})
            else:
                return http_400_response(u"用户名或手机不存在，请联系客服")

        else:
            return http_400_response(serializer.errors)


class UserResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = UserResetPasswordSerializer(data=request.DATA)
        if serializer.is_valid():
            data = serializer.data
            l = PasswordRecoverySMSLog.objects.filter(username=data["username"],
                                                      code=data["code"],
                                                      status=True,
                                                      expires_at__gte=int(time.time()))
            if l.exists():
                user = User.objects.get(username=data["username"])
                user.set_password(data["password"])
                user.save()
                l.update(status=False)
                return Response(data={"status": True})
            l.update(status=False)
            return http_400_response(u"验证码错误，请重新请求发送！")

        else:
            return http_400_response(serializer.errors)


class CaptchaView(APIView):
    def get(self, request):
        data = request.GET.get("data", None)
        if not data:
            captcha = Captcha(request)
            return captcha.display()
        else:
            return Response(data=request.session.get("_django_captcha_key", ""))

    def post(self, request):
        """检查是否需要验证码
        """
        username = request.DATA.get("username", None)
        return Response(data=check_is_need_captcha(username))


class UserView(APIView):
    def get(self, request):
        if not request.user.is_authenticated():
            return http_400_response("Login required")
        else:
            return Response(data=UserInfoSerializer(request.user).data)


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
#coding=utf-8
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from shop.models import Shop


def system_admin_required(view):
    """判断用户是超级管理员的修饰符，超级管理员拥有系统全部权限，注意区别shop_super_admin
    使用方法: @system_admin_required"""
    def check_user(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.is_staff and user.is_active:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return check_user


def shop_super_admin_required(view):
    """判断用户是否是商店的超级管理员，商店管理员拥有商店的全部管理权限，注意，is_staff的用户不受此限制
    在××kwargs里面获取到的shop_id 使用方法是@shop_super_admin_required
    """
    def check_user_permission(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/")
        shop_id = kwargs.get("shop_id", "-1")
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            raise Http404
        if request.user.is_staff or shop.shop_super_admin == request.user:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return check_user_permission


def shop_admin_required(view):
    """判断用户是不是商店的普通管理员，其权限低于系统管理员和商店超级管理员
    高权限用户不受影响
    """
    def check_user_permission(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/")
        shop_id = kwargs.get("shop_id", "-1")
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            raise Http404
        if request.user.is_staff or shop.shop_super_admin == request.user:
            return view(request, *args, **kwargs)
        if shop.admin.filter(username=request.user.username).exists():
            return view(request, *args, **kwargs)
        return HttpResponseRedirect("/login/")
    return check_user_permission


def get_csrf_protect(view):
    """为了防止get型csrf的发生，我们需要在参数中加入token参数，token的值应该和cookies里面的csrftoken的值一致
    使用方法 @get_csrf_protect
    """
    def check_token(request, *args, **kwargs):
        if request.method == "GET":
            get_token = request.GET.get("token", "-1")
            cookie_token = request.COOKIES.get("csrftoken", "0")
            if get_token == cookie_token:
                return view(request, *args, **kwargs)
        return HttpResponseForbidden(u"csrf验证失败")
    return check_token


def https_required(view):
    def check(request, *args, **kwargs):
        if request.is_secure():
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("https://" + request.get_host() + request.path)
    return check
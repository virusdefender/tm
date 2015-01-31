# coding=utf-8
from functools import wraps

from django.views.decorators.cache import patch_cache_control
from account.models import User

from rest_framework.response import Response


def login_required(view):
    @wraps(view)
    def _check(view_class, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return Response(data={"status": "error", "show": 0, "content": "Login required"}, status=401)
        return view(view_class, request, *args, **kwargs)

    return _check


def never_ever_cache(decorated_function):
    """Like Django @never_cache but sets more valid cache disabling headers.

    @never_cache only sets Cache-Control:max-age=0 which is not
    enough. For example, with max-axe=0 Firefox returns cached results
    of GET calls when it is restarted.
    """
    @wraps(decorated_function)
    def wrapper(*args, **kwargs):
        response = decorated_function(*args, **kwargs)
        patch_cache_control(
            response, no_cache=True, no_store=True, must_revalidate=True,
            max_age=0)
        return response
    return wrapper
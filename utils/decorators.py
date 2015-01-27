# coding=utf-8
from functools import wraps

from account.models import User

from rest_framework.response import Response


def login_required(view):
    @wraps(view)
    def _check(view_class, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return Response(data={"status": "error", "show": 0, "content": "Login required"}, status=401)
        return view(view_class, request, *args, **kwargs)

    return _check
#coding=utf-8
import json
from django.http import (Http404, HttpResponse)
from django.shortcuts import (redirect, render)
from django.views.decorators.csrf import csrf_exempt
from .upload_file import FileOperation
from .ueditor_config_json import ueditor_config_json


@csrf_exempt
def ueditor_config(request):
    parm = request.GET.get("action", "-1")
    if parm == "config":
        return HttpResponse(json.dumps(ueditor_config_json))
    elif parm == "uploadimage":
        f = FileOperation(request.FILES["upfile"])
        response = f.save()
        return HttpResponse(json.dumps(response))


def ueditor(request):
    return render(request, "ueditor_test.html")
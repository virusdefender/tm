# coding=utf-8
import redis
import requests
from rq.decorators import job


@job('sms', connection=redis.Redis(), timeout=10)
def send_sms(phone_number, content):
    accesskey = "2912"
    secretkey = "aee670d7603abee1c37bfda2ca1270fdeea4ff02"
    url = u"""sms.bechtech.cn/Api/send/data/json?accesskey=%s&secretkey=%s&mobile=%s&content=%s""" % (accesskey, secretkey, phone_number, content)
    try:
        r = requests.get("http://" + url)
    except Exception, e:
        pass


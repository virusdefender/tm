# coding=utf-8
import logging

import redis
import requests
from rq.decorators import job


@job('sms', connection=redis.Redis(), timeout=10)
def send_sms(phone_number, content):
    accesskey = "2912"
    secretkey = "aee670d7603abee1c37bfda2ca1270fdeea4ff02"
    url = u"""http://sms.bechtech.cn/Api/send/data/json?accesskey=%s&secretkey=%s&mobile=%s&content=%s""" % \
          (accesskey, secretkey, phone_number, content)
    logger = logging.getLogger("info_logger")
    try:
        r = requests.get(url)
        logger.debug(u"验证码短信发送结果:" + phone_number + r.content)
    except Exception, e:
        logger.debug(u"验证码短信发送失败:" + phone_number + content)


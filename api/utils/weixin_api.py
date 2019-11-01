# -*- coding: utf-8 -*-

from django.conf import settings
import json
import urllib.parse

from . import request_api


def get_openid(request_data):
    if 'appId' not in request_data:
        return None
    if 'appSecret' not in request_data:
        return None
    if 'code' not in request_data:
        return None

    url = settings.WE_SESSION_URL
    url = url.replace('$appid', request_data['appId'])
    url = url.replace('$secret', request_data['appSecret'])
    url = url.replace('$js_code', request_data['code'])
    data = request_api.get(url, 'application/json; charset=utf-8')

    if 'errcode' in data:
        return None
    return data['openid']
    pass

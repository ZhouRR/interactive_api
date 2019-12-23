# -*- coding: utf-8 -*-

from django.conf import settings

from . import request_api


def get_openid(request_data):
    # appId: 'wxb10693ce301b0503',
    # appSecret: 'fe966f7c89ba08eccd70060f2b3f9801',
    if 'appId' not in request_data:
        request_data['appId'] = 'wxb10693ce301b0503'
    if 'appSecret' not in request_data:
        request_data['appSecret'] = 'fe966f7c89ba08eccd70060f2b3f9801'
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

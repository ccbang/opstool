#!/bin/env python
# -*- coding:utf-8 -*-
'''
 @Author:      LBI
 @DateTime:    2016-08-10 17:14:49
 @Description:
'''
import time
import hashlib
import hmac
import random
from HTMLParser import parse

SecretId = 'xxxid'
# 注意这里所有操作需要腾讯云服务器主账号的SecretKey
SecretKey = 'xxxkey'


def get_all_machines(object):
    ''' 获得所有机器列表
    '''
    my_domain = 'cvm.api.qcloud.com'  # 服务器请求域名
    # 传说中的公共参数
    data = {
        "Action": 'DescribeInstance',
        "Region": 'gz',
        "Timestamp": int(time.time()),
        "Nonce": random.randint(0, 1024),
        "SecretId": SecretId,
    }
    url_title = '{0}/v2/index.php?'.format(my_domain)
    signTxt = generate_signtrue('GET', url_title, **data)
    data["Signature"] = signTxt
    end_agrvs = "&".join("{0}={1}".format(key, val) for key, val in data.items())
    endUrl = "https://" + url_title + end_agrvs
    return endUrl


def generate_signtrue(method, url, **kwargs):
    # 将字典按照键排序 计算hash值返回
    if isinstance(kwargs, dict):
        try:
            end = sorted(kwargs.items(), key=lambda ykey: ykey[0])
            urlOptions = '&'.join("{0}={1}".format(key, val) for key, val in end)
            endStr = "{0}{1}{2}".format(method, url, urlOptions)
            hmac_obj = hmac.new(SecretKey.encode(),
                                endStr.encode(),
                                digestmod=hashlib.sha1)
            ret = base64.b64encode(hmac_obj.digest())
            return parse.quote(ret)
        except Exception as e:
            print(e)
            return None
    else:
        return None


def search_domain(domain):
    '''获得对应域名信息
    '''
    get_domain = 'cns.api.qcloud.com'
    data = {
        "Action": 'DescribeResourceRecord',
        "Region": 'gz',
        "Timestamp": int(time.time()),
        "Nonce": random.randint(0, 1024),
        "SecretId": SecretId,
        "domain": domain
    }
    url_title = '{0}/v2/index.php?'.format(get_domain)
    signTxt = generate_signtrue('GET', url_title, **data)
    data["Signature"] = signTxt
    end_agrvs = "&".join("{0}={1}".format(key, val) for key, val in data.items())
    endUrl = "https://" + url_title + end_agrvs
    return endUrl

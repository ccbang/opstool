#!/bin/env python
# -*- coding:utf-8 -*-
'''
 @Author:      LBI
 @DateTime:    2016-08-10 17:14:49
 @Description:
'''
import os
from datetime import datetime
import hashlib
import random

SecretId = 'xxxid'
SecretKey = 'xxxkey'


def get_all_machines(object):
    my_domain = 'cvm.api.qcloud.com'  # 服务器请求域名
    # 传说中的公共参数
    data = {
        "Action": 'DescribeInstance',
        "Region": 'gz',
        "Timestamp": datetime.utcnow(),
        "Nonce": random.randint(0, 1024),
        "SecretId": SecretId,
    }
    signTxt = generate_signtrue('GET', my_domain, **data)


def generate_signtrue(method, url, **kwargs):
    # 将字典按照键排序 计算hash值返回
    fullUrl = '{0}/v2/index.php?'.format(url)
    if isinstance(kwargs, dict):
        try:
            end = sorted(kwargs, key=lambda ykey: ykey[0])
            endStr = "{0}{1}{2}".format(method, fullUrl, ''.join(end))
            mysha = hashlib.sha1()
            mysha.update(endStr.encode())
            has_ret = mysha.hexdigest()
            return has_ret
        except Exception as e:
            print(e)
            return None
    else:
        return None

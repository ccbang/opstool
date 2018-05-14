#!/bin/env python
# -*- coding:utf-8 -*-
'''
 @Author:      ccbang
 @DateTime:    2018-05-14 17:14:49
 @Description:
'''
from datetime import datetime, timedelta
import urllib
import json

CID = ''
SECURTKEY = ''


def send_to_weixin(msg, msg_type='warning'):
    ''' 根据警告类别发送给特定用户 '''
    host = 'https://qyapi.weixin.qq.com/cgi-bin'
    get_url = '{0}/gettoken?corpid={1}&corpsecret={2}'.format(
        host, CID, SECURTKEY
    )
    token_tmp = '/tmp/weixin_token'
    try:
        with open(token_tmp) as wf:
            last_time, token = wf.read().split()
    except Exception as e:
        print('read token err', e)
        two_hour_ago = datetime.now() - timedelta(seconds=7200)
        last_time = two_hour_ago.strftime('%s')
    if int(datetime.now().strftime('%s')) - int(last_time) > 7100:
        # get_data = requests.get(get_url, verify=True)
        get_data = urllib.request.urlopen(get_url).read()
        token_return = json.loads(get_data.decode())
        token = token_return.get('access_token', None)
        try:
            write_str = "{} {}".format(datetime.now().strftime('%s'), token)
            with open(token_tmp, 'w') as weixinf:
                weixinf.write(write_str)
        except Exception as e:
            print('write token err', e)
    tousers = get_users(msg_type)
    if token is not None:
        post_url = '{}/message/send?access_token={}'.format(host, token)
        data = {
            "toparty": '|'.join(map(str, list(tousers.keys()))),
            "msgtype": "text",
            "agentid": 1,
            "text": {
                "content": msg
            },
            "safe": "0"
        }
        send_msg = json.dumps(data, ensure_ascii=False)
        req = urllib.request.Request(post_url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('encoding', 'utf-8')
        ret = urllib.request.urlopen(post_url, send_msg.encode())
        if json.loads(ret.read().decode()).get('errcode') == 0:
            return True
        else:
            print(ret.read())
    return False


def get_users(msg_level='debug') -> dict:
    ''' return {partyID: userList} '''
    return {}

#!/bin/env python3
# -*- coding:utf-8 -*-
'''
@Author: ccbang 
@Date: 2018-05-15 14:58:48 
@Description:   
@Last Modified time: 2018-05-15 14:58:48 
'''
import json
import uuid
import os
import time
import ipaddress
import shutil


class Plogger:
    ''' 简单的打印，只为了调试，模仿logger的方法 '''

    def error(self, *args, **kwargs):
        print("error log {} {}".format(args, kwargs), flush=True)

    def debug(self, *args, **kwargs):
        print("debug log {} {}".format(args, kwargs), flush=True)

    def warning(self, *args, **kwargs):
        print("warning log {} {}".format(args, kwargs), flush=True)

    def info(self, *args, **kwargs):
        print("info log {} {}".format(args, kwargs), flush=True)


#################  json format ##########################
# >>> import NoIndent
# >>> import NoIndentEncoder
# >>> data = {
#     "online_list": NoIndent(list(range(10))),
#     "online_dict": NoIndent({k: v for k, v in enumerate(range(10))})
# }
# >>> print(json.dumps(data,cls=NoIndentEncoder, indent=2))
# {
#   "online_list": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
#   "online_dict": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9}
# }
# 如果需要写入文件则使用，
# 如果直接使用dump，不能达到预期效果，
# NoIndentEncoder需要重新改写iterencode方法，相对比较麻烦，仁者见仁，开心就好
# >>> print(json.dumps(data,cls=NoIndentEncoder, indent=2), file=open(file_name, 'w'))

class NoIndent(object):
    def __init__(self, value):
        self.value = value


class NoIndentEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super().default(o)

    def encode(self, o):
        result = super().encode(o)
        for k, v in self._replacement_map.items():
            result = result.replace('"@@%s@@"' % (k,), v)
        return result

################# end json format ##########################

################## centos 6 iptables #######################


def get_file_lock(lock_file):
    ''' 获取某个锁 '''
    step = 0
    while True:
        if not os.path.exists(lock_file):
            break
        if step > 30:
            return False
        step += 1
        time.sleep(5)
    os.system("touch {}".format(lock_file))
    return True


def release_lock(lock_file):
    ''' 删除锁文件 '''
    if os.path.exists(lock_file):
        os.remove(lock_file)
    return True


def iptable_tool(ip=None, port=None, logger=None):
    '''
    通过修改文件来配置防火墙
    为了冲突，写了个锁文件/tmp/.config_iptables
    :params port int
    '''
    config_file = "/etc/sysconfig/iptables"
    lock_file = '/tmp/.config_iptables'
    if not get_file_lock(lock_file):
        return False

    if logger is None:
        logger = Plogger()

    if ip is None or port is None:
        logger.error("开放端口或ip必须存在")
        return False
    # 检查参数类型
    try:
        if port is not None:
            int(port)
        if ip is not None:
            ipaddress.ip_address(ip)
    except Exception as e:
        logger.error("参数有问题 {}".format(e))
        return False

    now = time.strftime("%s", time.localtime())
    bak_ipf = "{}.bak_{}".format(config_file, now)
    if port is not None:
        new_line = (
            "-A INPUT -p tcp -m tcp"
            "--dport {} -j ACCEPT\n"
        ).format(int(port))
    if ip is not None:
        new_line = (
            "-A INPUT -m state"
            "--state NEW -m tcp -p tcp --source"
            "{} -j ACCEPT\n"
        ).format(ip)

    try:
        shutil.copy(config_file, bak_ipf)
        ins_index = []
        with open(config_file) as fd:
            data = fd.readlines()
        for line in data:
            if new_line == line:
                logger.debug('allow rule is in iptable')
                ret = True
                return  # 结束try 跳到finally
            elif line.startswith('-A INPUT'):
                ins_index = fd.index(line)
        data.insert(ins_index, new_line)
        with open(config_file, 'w') as sf:
            sf.writelines(fd)
        ipt_restart = '/etc/init.d/iptables restart'
        if os.system(ipt_restart) == 0:
            release_lock(lock_file)
            logger.debug('restart iptables success')
            ret = True
        else:
            logger.error("can not restart iptables")
            ret = False
    except Exception as e:
        print(__name__, e)
        logger.error('can not read iptables config')
        ret = False
    finally:
        release_lock(lock_file)
        return ret


def iptabel_cmd_tool(ip=None, port=None, logger=None, store=False):
    ''' 
    通过iptables 命令增加临时防火墙配置
    : params store 是否将现在保存到配置文件
    '''
    if logger is None:
        logger = Plogger()
    if ip is None or port is None:
        logger.error("开放端口或ip必须存在")
        return False
    # 检查参数类型
    try:
        if port is not None:
            int(port)
        if ip is not None:
            ipaddress.ip_address(ip)
    except Exception as e:
        logger.error("参数有问题 {}".format(e))
        return False

    if port is not None:
        cmd_line = (
            "-p tcp -m tcp"
            "--dport {} -j ACCEPT"
        ).format(int(port))
    if ip is not None:
        cmd_line = (
            "-m state"
            "--state NEW -m tcp -p tcp --source"
            "{} -j ACCEPT"
        ).format(ip)
    # 检查规则是否在内
    check_cmd = 'iptables -C INPUT {}'.format(cmd_line)
    if os.system(check_cmd) == 0:
        logger.debug("规则已经存在")
    else:
        # 将规则插入第一条
        add_cmd = "iptables -I INPUT 1 {}".format(cmd_line)
        if os.system(add_cmd) != 0:
            logger.error("增加规则{}时发生错误".format(add_cmd))
            return False
        logger.debug("成功增加规则{}".format(add_cmd))
    if store:
        cmd = 'iptables-save >/etc/sysconfig/iptables'
        if os.system(cmd) == 0:
            logger.debug("保存规则成功")
        else:
            logger.error("保存规则失败")
    return True

################## end centos 6 iptables #######################

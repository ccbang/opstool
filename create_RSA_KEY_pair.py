#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 @Author:      w38351479
 @DateTime:    2016-08-31 11:16:52
 @Description:   功能：用于生成密钥对和打印私钥指纹
 @Depend:  pip install pycrypto
           源码安装  paramiko
'''
import paramiko
import StringIO
import os

def gen_keys(key_user='root',key_name='id_rsa',key=""):
    """ 
    生成公钥 私钥 
    """
    output_dir = '/data/python'
    output_file = ''.join([output_dir,'/',key_name])
    output_filepub = ''.join([output_file,'.pub'])
    output_filepub_f = file(output_filepub, 'w')
    key_content = {}
    sbuffer = StringIO.StringIO()
    #生成私钥 
    if not key:
        try:
            key = paramiko.rsakey.RSAKey.generate(2048)
            key.write_private_key_file(output_file)
        except IOError:
            raise IOError('gen_keys: there was an error writing to the file')
        except SSHException:
            raise SSHException('gen_keys: the key is invalid')
    else:
        private_key = key
        try:
            key = paramiko.rsakey.RSAKey.from_private_key_file(private_key)
        except SSHException, e:
            raise SSHException(e)
    #获取私钥的名字ssh-rsa，空格，公钥，自定义用户名@主机名  
    for data in [key.get_name(),
                 " ",
                 key.get_base64(),
                 " %s@%s" % (key_user, os.uname()[1])]:
        sbuffer.write(data)

    public_key = sbuffer.getvalue()
    output_filepub_f.write(public_key)
    output_filepub_f.close()

def get_key_finger(key=""):
    '''
            获取私钥指纹
    '''
    from binascii import hexlify
    if not key:
        private_key_path = '/root/.ssh/id_rsa'
    else:
        private_key_path = key
    try:
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        return hexlify(key.get_fingerprint())
    except Exception:
        print 'Error: key file is not exist'
        return False

gen_keys()
finger_p = get_key_finger()
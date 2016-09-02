#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 @Author:      w38351479
 @DateTime:    2016-09-01 00:01:26
 @Description:   根据使用key登陆，返回当前ssh连接的所属用户指纹注释；剩下的设置shell行为的几条外部命令没写。。。。
 @Depend:  
'''
import os
import psutil
import re
import sys
#from binascii import hexlify
#import paramiko

def get_py_ppid():
    '''
            根据python当前PID获取父进程sshd的进程号，用于后面匹配公钥指纹
    '''
    #查找父进程（python建立在sshd之上，所以我要找的是sshd的子进程号（不是sshd的主进程））,需要多层查找，直至父进程为1
    py_pid = os.getpid()
    py_ppids = psutil.Process(py_pid).ppid()
    #最后会查找到父进程为1为止
    while py_ppids != 1:
        py_ppid = psutil.Process(py_ppids).ppid()
        py_pname = psutil.Process(py_ppids).name()
        #首次出现sshd进程时就返回
        if py_pname == 'sshd':
            py_ppid = py_ppids
            break
        else:
            py_ppids = py_ppid
            
    return py_ppid




#========================================
def from_ssh_pid_get_key(py_ppid=''):
    '''
        根据前面函数获取的ppid，找出对应公钥指纹，并返回
    '''
    if not py_ppid:
        print 'error: is not get python for shell ppid'
        sys.exit(1)
    f = open('/var/log/secure')
    #往前推10000个字节，或全部
    f_s = os.stat('/var/log/secure')
    if f_s.st_size > 200000:
        f.seek(-200000,2)
    else:
        f.seek(0)
    flag_t = True
    while flag_t:
        read_line_text = f.readline()
        if read_line_text == '':
            break
        #查找关键字
        find_RSA = read_line_text.find('RSA')
        find_sshd = read_line_text.find('sshd')
        #sshd和RSA必须存在
        if find_RSA != -1 and find_sshd != -1:
            find_list = read_line_text.split()
            find_list.reverse()
            #列表翻转后，第一个元素就是key
            login_key = find_list[0]
            #遍历列表，查找sshd关键字位置，并且提取sshd进程号
            for i in range(len(find_list)):
                if re.search('sshd',find_list[i]):
                    #列表形式返回提取到的sshd pid
                    sshd_pid_key_list = re.findall('\d+',find_list[i])
                    sshd_pid = int(sshd_pid_key_list[0])
                    '''
                                                    如果这里获取到的pid和前面提取的py_ppid一样，那么就返回key
                    '''
                    if py_ppid == sshd_pid:
                        sshd_pid_key = login_key
                        flag_t = False
                        break
                    else:
                        sshd_pid_key = ''
    f.close()
    return sshd_pid_key


#========================================日志过滤，获取sshd和指纹对应列表
'''
#每次的一个secure登陆日志RSA记录数据列表都重新设置重新查找公钥列表，以便计算指纹
['07:b8:66:86:f2:e7:c8:29:20:62:7a:b9:b7:0d:99:11', '\xe9\x82\x93\xe5\x90\xaf\xe5\xbf\x97', 'ce:11:d5:a2:50:d9:08:5a:4b:d8:a0:3e:bb:84:76:2f', '\xe5\x85\xac\xe7\x94\xa8']
'''
def get_pub_finger(pub_key_path='/root/.ssh/authorized_keys',sshd_pid_finger=''):
    '''
        由上面提供的公钥指纹找到是属于谁的指纹
    '''
    f_pub = open(pub_key_path)
    for i in f_pub.readlines():
        #轮序计算公钥
        key_n = i
        #python好像没有相关函数或模块可以根据公钥生成指纹
#         key_nn = paramiko.PKey(key_n)
#         print key_n
#         pub_key_finger =  hexlify(key_nn.get_fingerprint())
#         print pub_key_finger
        if len(key_n) > 210:
            #找到ssh-rsa开头的才进行打印指纹，已经注释的不进行解释
            result1 = len(re.findall('^ssh-rsa',key_n,re.MULTILINE))
            if result1 == 1:
                key_f = "/tmp/.key_test"
                fp = open(key_f,'w')
                fp.write(key_n)
                fp.close()
                os.system("/usr/bin/ssh-keygen -lf %s |awk '{print $2}' > /tmp/.key_print" % (key_f))
                f_pub_f = open('/tmp/.key_print')
                #需要褪去换行符
                f_pub = f_pub_f.read().strip()
                f_pub_f.close()
                '''
                                        如果这里获取到的指纹和函数变量提供的一致，那么就是该用户的所属指纹
                '''
                if f_pub == sshd_pid_finger:
                    key_name = key_n.split()[2]
                    break
                else:
                    key_name = 'Find Not'

    return key_name
    f_pub.close()

if __name__ == '__main__':
    user_key = from_ssh_pid_get_key(py_ppid=get_py_ppid())
    print get_pub_finger(sshd_pid_finger=user_key)

#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
 @Author:      w38351479
 @DateTime:    2016-09-05 16:29:02
 @Description:   
#need environment:
1)yum -y install gcc gcc-c++ libffi-devel python-devel openssl-devel  mysql-devel libxml2 libxml2-dev libxslt* zlib openssl ; and other [mysql mysql-devel]
2)you ensure "mysql_config" in environment path can find
3)python version should be >= 2.7
4)mkdir -p /data/export_excel
5)pip install mysql
 @Depend:  
'''

import MySQLdb
import xlsxwriter
import time
import getpass
import sys
# it's different between workbook and worksheet
pass_r = getpass.getpass('Please input mysql password:')
#connect to mysql
try:
    conn = MySQLdb.connect(host="localhost",user="root",passwd=pass_r,db="gxtlog",use_unicode=1,charset='utf8')
    cur = conn.cursor()
except Exception,e:
    print Exception,":",e
    print "\033[31mMySQL数据库密码错误！\033[0m"
    sys.exit(1)

# query sql
sql = "select * from gw_app;"
try:
    data = cur.execute(sql)
except Exception,e:
    print Exception,":",e
    sys.exit(1)

# use fetchall method to get a list, some tuples in it
try:
    data_list = cur.fetchall()
except Exception,e:
    print Exception,":",e

fields = cur.description
cur.close()
conn.close()


export_file = '/data/export_excel/'+str(time.strftime("%Y%m%d%H%M"))+'.xlsx'
workbook = xlsxwriter.Workbook(export_file)    #创建一个Excel文件
worksheet = workbook.add_worksheet()    #创建一个工作表对象

#worksheet name(you can set)
worksheet.title = 'data'

rows = len(data_list)
cols = len(data_list[0])
# same as read data

#output title and data
for ifs in range(cols):
    worksheet.write(0, ifs ,fields[ifs][0])  #刚好标题是0行开始，那么内容就从1开始写
for rx in range(1,rows+1):
    for cx in range(cols):
        worksheet.write(rx, cx, data_list[rx-1][cx])

workbook.close()
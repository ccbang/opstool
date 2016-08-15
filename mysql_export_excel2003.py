#!/usr/bin/env python  
#coding=utf-8  
#确保：
#1）/usr/bin/mysql_config需要存在并能直接找到命令位置
#2) yum install ncurses-devel python-devel -y
#3）pip install xlwt
#4）pip install mysql
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import xlwt
import time
import MySQLdb

conn=MySQLdb.connect(host='localhost',user='root',passwd='xxxx',db='test',charset='utf8')  
cursor=conn.cursor()  
count = cursor.execute('select * from log_201606')
  
print 'has %s record' % count  
#重置游标位置  
cursor.scroll(0,mode='absolute')  
#搜取所有结果  
results = cursor.fetchall()  
#测试代码，print results  
#获取MYSQL里的数据字段  
fields = cursor.description  
#将字段写入到EXCEL新表的第一行  
wbk = xlwt.Workbook()  
sheet = wbk.add_sheet('gxtlog',cell_overwrite_ok=True)  
for ifs in range(0,len(fields)):  
    sheet.write(0,ifs,fields[ifs][0])  
ics=1  
jcs=0  
for ics in range(1,len(results)+1):  
    for jcs in range(0,len(fields)):  
        sheet.write(ics,jcs,results[ics-1][jcs])
wbk.save('/data/export_excel/'+str(time.strftime("%Y%m%d%H%M"))+'.xls')

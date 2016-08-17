#!/usr/bin/env python
#_*_ coding:utf-8 _*_

'''
 @Author:      w38351479
 @DateTime:    2016-08-17 10:14:50
 @Description: nginx日志分析;主要功能：统计状态码/统计访问IP/网站访问流量统计/网站分钟级请求数统计
'''

#Python 编写多步的 MapReduce 作业(可用于Hadoop)
#pip install MRjob

from mrjob.job import MRJob
from mrjob.step import MRStep
import re

#统计状态码==============================
class MRCounter_status(MRJob):
    def mapper(self, key, line):
        i = 0
	for httpcode in line.split():
            #状态码位于第几列
	    if i==8 and re.match(r"\d{1,3}", httpcode):
       	    #获取日志的http状态码字段,放到yield迭代器里
	        yield httpcode, 1
	        #初始化key:value, value计数为1
	    i+=1
    #相同状态码叠加
    def reducer(self, httpcode, occurrences):
        yield httpcode, sum(occurrences)
	#对排序后的key对应的value做sum累加
    #平时你不分步也可以的
    def steps(self):
        return [MRStep(mapper=self.mapper), 
                MRStep(reducer=self.reducer)]
        
#统计访问IP==============================
#IP匹配规则
IP_RE = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
class MRCounter_IP(MRJob):
    def mapper(self, key, line):
        #i匹配IP正则后生成key:value,其中key为IP，value初始值为1
        for ip in IP_RE.findall(line):
            yield ip, 1
    def reducer(self, ip, occurrences):
        yield ip, sum(occurrences)
    def steps(self):
        return [MRStep(mapper=self.mapper),
                MRStep(reducer=self.reducer)]

#网站访问流量统计========================
class MRCounter_flow(MRJob):
    def mapper(self, key, line):
        i = 0
        for flow in line.split():
            if i==3:       #获取访问时间段
                timerow = flow.split(":")
                hm = timerow[1]+":"+timerow[2]    #获取“小时:分钟”作为key
            if i==10 and re.match(r"\d{1,}", flow):   #获取日志第11列——发送字节数
                yield hm, int(flow)
                #初始化key:value
            i+=1
    def reducer(self, key, occurrences):
        yield key, sum(occurrences)
        #相同key"小时:分钟"的value做sum累加

#网站分钟级请求数统计====================
class MRCounter_dt(MRJob):
    def mapper(self, key, line):
        i = 0
        for dt in line.split():
            if i==3:       #获取访问时间段
                timerow = dt.split(":")
                hm = timerow[1]+":"+timerow[2]    #获取“小时:分钟”作为key
                yield hm, 1
                #初始化key:value, value计数为1
            i+=1
    def reducer(self, key, occurrences):
        yield key, sum(occurrences)



if __name__ == '__main__':
    MRCounter_status.run()
    MRCounter_IP.run()
    MRCounter_flow.run()
    MRCounter_dt.run()

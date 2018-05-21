#!/bin/bash
# @Author: ccbang 
# @Date: 2018-05-21 10:44:51 
# @Description:   用来接收shell管道输出
# @Last Modified time: 2018-05-21 10:44:51 
# example:
# tail -f /var/message |sh pipeShell.sh
# 可以处理每一行

# 如果存在参数sh pipeShell.sh filename
# 则将标准输入指向参数
if [ $# -gt 0 ];then
   exec 0<$1;
fi

# 如果不带参数则直接获取系统标准输入，即管道内容
while read line; do
    echo $line
done<&0;
# 通过标准输入循环读取内容

# 这里关闭描述符
exec 0&-;
 
#!/bin/bash

date_week=`date +%w`
DATE=`date +%Y%m%d`
USER=ftpget
PASSWD='passwd'
IP='1.1.1.1'
PORT=5678

DST_PATH=/data/innoback
#数据库原密码：
mysql_passwd='123pass'
#root用户更新密码为：
mysql_passwd1='456pass'

#数据库默认管理用户：
mysql_user=root


#--------------------------------------------------------
#释放内存
/bin/bash /data/shell/release_memory.sh

#从FTP获取当天备份数据
function get_data(){
if [ ! -d $DST_PATH ];then
	mkdir -p  $DST_PATH
fi

if [ ! -f /usr/bin/lftp ];then
	yum -y install lftp
fi

cd $DST_PATH
/usr/bin/lftp -c "pget -n 8  ftp://$USER:$PASSWD@$IP:$PORT/BI_add_mysql_$DATE.zip" 
sleep 1

if [ -f $DST_PATH/BI_add_mysql_$DATE.zip.lftp-pget-status ];then
	echo "$DST_PATH/BI_add_mysql_$DATE.zip文件没有下载完成"
	exit 1
fi
}

#备用方案--------------------------------------------------
function rsync_get_data(){
if [ ! -d $DST_PATH ];then
        mkdir -p  $DST_PATH
fi
echo '启用rsync下载备用方案'
/usr/bin/rsync -auvzP  --password-file=/data/shell/rsyncd_mysql_ftp.pass --port=8873 root@$IP::mysql_ftp/BI_add_mysql_$DATE.zip $DST_PATH/
}
#-----------------------------------------------------------

#解压增量备份
function unzip_data(){
if [ -f $DST_PATH/BI_add_mysql_$DATE.zip ];then
	cd $DST_PATH 
	/usr/bin/unzip -q BI_add_mysql_$DATE.zip -d $DST_PATH/ftp_back/add/ 
fi
}



#还原全备份、增量备份
function innobackupex_data_full(){
	cd $DST_PATH
	if [ -d base_20160803 ];then
		mv base_20160803 $DST_PATH/ftp_back/full/
	else
		echo "$DST_PATH/base_20160803全备包不存在,重新解压"
		/bin/date
	        echo '开始前台解压全备包'
	        cd $DST_PATH
	        #rm -rf $DST_PATH/base_20160803
	        /bin/bash /data/shell/release_memory.sh
	        /usr/bin/unzip -q base_20160803.zip
		mv base_20160803 $DST_PATH/ftp_back/full/
		
	fi
	if [ ! -d $DST_PATH/ftp_back/add/BI_add_mysql_$DATE ];then
		echo "找不到已解压的增备包"
		exit 1
	fi
	#停止mysql，清掉mysqldata
	/bin/date
	echo '停止mysql，清掉mysqldata'
	NUM_MYSQL=`ps uax |grep mysqld |grep 'webapps' |grep -v 'grep' |wc -l`
        if [ "$NUM_MYSQL" -gt "0" ];then
		/etc/init.d/mysqld stop
	fi
	NUM_MYSQL=`ps uax |grep mysqld |grep 'webapps' |grep -v 'grep' |wc -l`
	if [ "$NUM_MYSQL" -gt "0" ];then
		ps uax |grep mysqld |grep 'webapps' |grep -v 'grep' |awk '{print $2}' |xargs kill -9
	fi
	sleep 2
	rm -rf /data/mysqldata/data
	#还原全备日志
	echo '还原全备日志'
	echo "/usr/bin/innobackupex --defaults-file=/etc/my.cnf --user=bkpuser --use-memory=2G --parallel=4 --apply-log --redo-only $DST_PATH/ftp_back/full/base_20160803"

	/usr/bin/innobackupex --defaults-file=/etc/my.cnf --user=bkpuser --use-memory=2G --parallel=4 --apply-log --redo-only $DST_PATH/ftp_back/full/base_20160803

	#####还原所有增备日志(只有自带增备日志和全备至今的增备日志，共两个)
	#当前只有一个
	FILE_LIST=`ls  $DST_PATH/ftp_back/add |sort`
	LAST_ADD=`ls -l $DST_PATH/ftp_back/add|awk '{print $NF}' |sed 1d |sort |tail -n 1`

	for line in $FILE_LIST;do
		if [ "$line" == "$LAST_ADD" ];then
			/usr/bin/innobackupex --defaults-file=/etc/my.cnf  --user=bkpuser --use-memory=2G --parallel=4 --apply-log $DST_PATH/ftp_back/full/base_20160803 --incremental-dir=$DST_PATH/ftp_back/add/$line
			#状态监测
			if [ "$?" -eq '0' ];then
				echo "/usr/bin/innobackupex --defaults-file=/etc/my.cnf  --user=bkpuser --use-memory=2G --parallel=4  --apply-log $DST_PATH/ftp_back/full/base_20160803 --incremental-dir=$DST_PATH/ftp_back/add/$line"
				echo "$line增备还原成功"
			else
				echo "$line增备还原失败"
				exit 1
			fi
		else
			/usr/bin/innobackupex --defaults-file=/etc/my.cnf  --user=bkpuser --use-memory=2G --parallel=4 --apply-log --redo-only $DST_PATH/ftp_back/full/base_20160803 --incremental-dir=$DST_PATH/ftp_back/add/$line

			echo "/usr/bin/innobackupex --defaults-file=/etc/my.cnf  --user=bkpuser --use-memory=2G --parallel=4  --apply-log --redo-only $DST_PATH/ftp_back/full/base_20160803 --incremental-dir=$DST_PATH/ftp_back/add/$line"
		fi
	done

	#还原数据
	#/usr/bin/innobackupex --defaults-file=/etc/my.cnf --user=bkpuser --use-memory=1G --parallel=4 --copy-back $DST_PATH/ftp_back/full/base_20160803
	/bin/date
	echo '移动数据，及修改权限'
	mv $DST_PATH/ftp_back/full/base_20160803 /data/mysqldata/data
	chown -R mysql.mysql /data/mysqldata/data
	#为确保能启动，清除日志
	rm -f /data/mysqldata/data/ib_logfile*
}


#增加数据库用户授权与删除敏感数据
function update_mysqluser(){
/bin/date
echo '开启数据库'
/etc/init.d/mysqld start
if [ "$?" -eq "0" ];then
	rm -rf $DST_PATH/ftp_back/full/*
	rm -rf $DST_PATH/ftp_back/add/*
fi
/bin/date
echo '创建新账号，修改密码，删除敏感数据'

/usr/bin/mysql -u$mysql_user -p$mysql_passwd <<  EOF
UPDATE mysql.user SET password=password('$mysql_passwd1')  WHERE user='root'; 
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY  '$mysql_passwd1' with grant option;
flush privileges;
use test
source /data/shell/mysql_view.sql;
quit
EOF



}

#清除增量备份包
function clear_zip_data(){
	/bin/date
	echo '清除增量备份包'
	DEL_LIST=`/usr/bin/find $DST_PATH -name "BI_add_mysql_20*.zip" -type f -mtime +3`
	echo "$DEL_LIST"
	/usr/bin/find $DST_PATH -name "BI_add_mysql_20*.zip" -type f -mtime +3 -exec rm -rf {} \;
}
#解压全备文件包
function mysql_data_full(){
	/bin/date
	echo '开始后台解压全备包'
	cd $DST_PATH
	rm -rf $DST_PATH/base_20160803
	/bin/bash /data/shell/release_memory.sh
	/usr/bin/unzip -q base_20160803.zip &
}

################################################函数调用####################
##从公网获取当天备份数据
#下载方案一（ftp）
#get_data
#下载方案二（rsync）
rsync_get_data
wait
sleep 5
#解压当天数据
unzip_data
###合并增量备份日子，并还原数据库
innobackupex_data_full
##清除2天前增量备份数据压缩包
clear_zip_data
##数据库用户授权，清除敏感数据
update_mysqluser
##解压全备文件包，等待下次备用
mysql_data_full
/bin/date

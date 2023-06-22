#!/bin/bash

#服务器执行
project=bookmarkSpider
from=/home/ubuntu
to=/home/$project

#创建目录
mkdir -p $to

if [ -e $from/$project.zip ]
then
    unzip $from/$project.zip > /dev/zero
    rm -fr $to/*
    cp -fr $from/$project/* $to
    rm -fr $from/$project
fi

#spider path
spiderPath=$to/bookmarkSpider
cp $spiderPath/server/settings.py $spiderPath
cd $spiderPath

#ps aux | grep -ie python3 | awk '{print $2}' | xargs kill -9
##杀死进程，这个命令更准确##
pkill -f python3

#启动爬虫
nohup python3 start.py >> /dev/zero &

echo "Spider start....."
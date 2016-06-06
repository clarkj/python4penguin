#!/bin/sh
PATH=$PATH:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
killall watch
dir=/home/pi/Desktop/python
cd $dir
# /usr/bin/watch --precise -n 4 $dir/modcache.py > /dev/null 2>&1 &
nohup /usr/bin/watch --precise -n 4 ./modcache.py 2>&1 &

#!/bin/sh
killall watch
cd /home/pi/Desktop/python
#nohup watch --precise -n 4 ./modcache.py > /dev/null 2>&1 &
nohup watch --precise -n 4 ./modcache.py 2>&1 &

#! /bin/bash

case "$(pidof -x looper.sh | wc -w)" in

0)  echo "restarting looper.sh     $(date)" >> /home/pi/looperlog.txt
    cd /home/pi/Desktop/python && ./looper.sh > /home/pi/looperreallog.txt &
    ;;
1)  # all ok
    ;;
*)  echo "Removed double looper: $(date)" >> /home/pi/looperlog.txt
    kill $(pidof -x looper.sh | awk '{print $1}')
    ;;
esac

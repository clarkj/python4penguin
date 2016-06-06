#!/bin/sh
wait=3.0
slop=0.02
file=go.loop
touch $file
while test -f $file
do
  start=`date +%s.%N`
  ./modcache.py > /home/pi/hifile4.txt
  # test arbitrary
  date +%S.%N
  finis=`date +%s.%N`
  total=`echo "$wait - ($finis - $start) - $slop"|bc`
  if [ 0 -eq "$(echo "$total < 0.0"|bc)" ]
  then
    # echo total above zero $total
    sleep $total
  fi
done

# echo $total

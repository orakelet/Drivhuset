#!/bin/bash
#
# Sjekker om auto_water.py er startet
# hvis ikke blir den startet
#
cd /home/pi/Python
d=`date +'%Y/%m/%d %H:%M:%S'`
echo $d [Sjekk]  Sjekker auto_water  >>/home/pi/Python/auto_water.log 2>&1
running=`ps -ef|grep python|grep auto_water.py|wc -l`
if [ $running -eq 0 ]; then
    echo $d [Sjekk]  auto_water.py er ikke startet  >>/home/pi/Python/auto_water.log 2>&1
    /home/pi/Python/python3 auto_water.py& >>/home/pi/Python/auto_water.log 2>&1
    echo $d [Sjekk] Nå er auto_water.py startet  >>/home/pi/Python/auto_water.log 2>&1
else
    echo $d [Sjekk] auto_water.py går >>/home/pi/Python/auto_water.log 2>&1
fi

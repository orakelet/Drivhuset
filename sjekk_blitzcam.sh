#!/bin/bash
d=`date +'%Y/%m/%d %H:%M:%S'`
running=`ps -ef|grep python|grep blitzcam|wc -l`
if [ $running -eq 0 ]; then
    echo $d [Sjekk] Blitzcam har stoppet >>/home/pi/OneDrive/Python/Drivhuset/blitzcam.log
    python /home/pi/OneDrive/Python/Drivhuset/blitzcam.py -c /home/pi/OneDrive/Python/Drivhuset/lokal.json &
    echo $d [Sjekk] Blitzcam restartet >>/home/pi/OneDrive/Python/Drivhuset/blitzcam.log
else
    echo $d [Sjekk] Blitzcam kjører
fi

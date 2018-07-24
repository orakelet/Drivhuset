#!/bin/bash
#
# Sjekker om onedrive-d er startet
# hvis ikke blir den startet
# hvis den går blir den restartet
#
d=`date +'%Y/%m/%d %H:%M:%S'`
echo $d [Sjekk]  Sjekker OneDrive  >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
printenv | grep USER >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
export USER='pi' # env-variabel ikke satt når startet fra crontab
running=`ps -ef|grep python|grep onedrive-d|wc -l`
/usr/local/bin/onedrive-d status >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
env >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
if [ $running -eq 0 ]; then
    echo $d [Sjekk]  OneDrive er ikke startet  >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
    /usr/local/bin/onedrive-d start >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
    echo $d [Sjekk] Nå er OneDrive startet  >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
else
    /usr/local/bin/onedrive-d restart >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
    echo $d [Sjekk] OneDrive er restartet >>/home/pi/OneDrive/Python/Ute/onedrive.log 2>&1
fi

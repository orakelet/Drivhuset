# -*- coding: utf-8 -*-
import logging
import unicodedata
import paho.mqtt.publish as publish
import time
import datetime
import Adafruit_DHT as dht
host='steine.mine.nu'
logfil='/home/pi/OneDrive/Python/Ute/dht22.log'
logform='%(asctime)s %(message)s'
dateString = '%Y/%m/%d %H:%M:%S'
logging.basicConfig(filename=logfil, format=logform, datefmt=dateString, level=logging.INFO)

humidity, temperature = dht.read_retry(dht.DHT22,22)
print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
logging.debug('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
temp = str(round(temperature,1))
logging.debug('Temp=%s', temp)
humid = str(round(humidity,1))
logging.debug('Humid=%s', humidity)
logging.debug('%s : temp = %s, fukt = %s',datetime.datetime.now().strftime(dateString),temp,humid)
payload=[{'topic':"Ute/temp",'payload':temp},{'topic':"Ute/fukt",'payload':humid}]
logging.info (payload)
ret=publish.multiple(payload, hostname=host)
logging.info(ret)

# -*- coding: utf-8 -*-
# Sjekk fuktighet i jorden
#   Bruk ADC for bedre kontroll på verdiene
#   Display som viser fuktighet?
# Kjør pumpen en liten stund
#   Bruk rele for å styre pumpen
# Rapporter til MQTT
# Sjekk hvert 5. minutt
# tilpass til mønsteret i web_plants (water.py)
#
import logging
import paho.mqtt.publish as publish
import argparse
import warnings
import RPi.GPIO as GPIO
import quick2wire.i2c as i2c
import time
#
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
args = vars(ap.parse_args())
#
# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
loglevel = getattr(logging, (conf["loglevel"]).upper())
client = None
#
class TempImage:
    def __init__(self, basepath=conf["basepath"], ext=".jpg"):
        # construct the file path
        # datestring = time.strftime("%Y%m%d-%H%M%S")
        self.path = "{base_path}/{date_String}{ext}".format(base_path=basepath,
                                                            date_String=conf["user"], ext=ext)

    def cleanup(self):
        # remove the file
        os.remove(self.path)
#
#I2C-addresses:
address = conf["address"]
iodir_register = conf["iodir_register"]
gpio_register = conf["gpio_register"]
#
# Pin-tilordning:
fukt = conf["fukt"]
pumpe = conf["pumpe"]
GPIO.setmode(GPIO.BCM)
GPIO.setup(fukt, GPIO.IN)
GPIO.setup(pumpe, GPIO.OUT)
#
host=conf["host"]
logfil=conf["basepath"] + conf["logfil"]
logform=conf["logform"]
dateString =conf["%Y/%m/%d %H:%M:%S"]
#
#
print("[INFO] Loglevel: {} til {} ".format(loglevel, logfil))
#logging.basicConfig(filename='pi_surveillance.log',level=loglevel,format='%(asctime)s %(message)s')
logging.basicConfig(filename=logfil, format=logform, datefmt=dateString, level=loglevel)

if conf["OneDrive"]:
	logging.info("[INFO] Using OneDrive")

if conf["mqtt"]:
	logging.info("[INFO] Sending statistics to MQTT")

# QuickWire eksempelkode hvis vi skal bruke ADC
# Uten ADC får vi bare "Tørt/Vått", med ADC får vi graden av fukt
# Se "GPIO RPi Wiring.jpg"
with i2c.I2CMaster() as bus:
    bus.transaction(
        i2c.writing_bytes(address, iodir_register, 0xFF))

    read_results = bus.transaction(
        i2c.writing_bytes(address, gpio_register),
        i2c.reading(address, 1))

    gpio_state = read_results[0][0]

    print("%02x" % gpio_state)
# Build a payload for MQTT and send it
# Fuktigheten har vi nettopp funnet, hva med temp/humidity fra DHT22?
if conf["mqtt"]:
    topic = conf["topic"] + "/fukt"
    payload = [{'topic': topic, 'payload': gpio_state}]
    ret = publish.multiple(payload, hostname=conf["host"])





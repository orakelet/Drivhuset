# External module import
import RPi.GPIO as GPIO
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import datetime
import time

init = False
# Create an ADS1015 ADC (12-bit) instance.
adc = Adafruit_ADS1x15.ADS1015()
POTTE = 0 # LitenAgurk
KAR = 1
StorAgurk = 1
LitenPumpe = 7
StorPumpe = 8
GAIN = 1
DRY = 800

GPIO.setmode(GPIO.BOARD)  # Broadcom pin-numbering scheme


def get_last_watered():
    try:
        f = open("last_watered.txt", "r")
        return f.readline()
    except:
        return "NEVER!"


def get_status(pin=0):
    wet = adc.read_adc(pin, gain=GAIN)
    if wet > DRY:
        return 1 # Tørr
    else:
        return 0 # Våt

def get_moisture(pin=0):
    wet = adc.read_adc(pin, gain=GAIN)
    return wet

def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
#    GPIO.output(pin, GPIO.HIGH)


def auto_water(delay=10, pump_pin=7):
#    consecutive_water_count = 0
    init_output(pump_pin)
    print("Here we go! Press CTRL+C to exit")
    try:
        while True:
            time.sleep(delay)
            wet = get_status(POTTE) == 0
            bay = get_status(KAR) == 0 # skal være FALSE/1
            if not wet and bay: #
#                if consecutive_water_count < 5:
                    pump_on(pump_pin, 5)
#                consecutive_water_count += 1
#            else:
#                consecutive_water_count = 0
    except KeyboardInterrupt:  # If CTRL+C is pressed, exit cleanly:
        GPIO.cleanup()  # cleanup all GPI


def pump_on(pump_pin=7, delay=5):
    init_output(pump_pin)
    f = open("last_watered.txt", "w")
    f.write("Last watered {}".format(datetime.datetime.now()))
    f.close()
    GPIO.output(pump_pin, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(pump_pin, GPIO.LOW)

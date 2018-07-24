# -*- coding: utf-8 -*-
#
# Laste inn bilde fra kamera og sende det på SFTP til server
#
import time
import datetime
import json
import os
import cv2
import pysftp
import argparse
import warnings
import logging
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
#
loglevel = getattr(logging, (conf["loglevel"]).upper())
logfil=conf["basepath"] + "/" + conf["logfil"]
logform=conf["logform"]
dateString=conf["dateString"]
logging.info("[INFO] Tar bilde")
client = None
print("[INFO] Loglevel: {} til {} med {}".format(loglevel, logfil, logform))
# logging.basicConfig(filename='pi_surveillance.log',level=loglevel,format='%(asctime)s %(message)s')
logging.basicConfig(filename=logfil, format=logform, datefmt=dateString, level=loglevel)


class TempImage:
    def __init__(self, basepath=conf["basepath"], ext=".jpg"):
        # construct the file path
        datestring = time.strftime("%Y%m%d-%H%M%S")
        self.path = "{base_path}/{date_String}{ext}".format(base_path=basepath,
                                                            date_String=datestring, ext=ext)

    def cleanup(self):
        # remove the file
        os.remove(self.path)


#
srv = pysftp.Connection(host=(conf["host"]), username=(conf["user"]), password=(conf["up"]))
#
ret = False
while not ret:
   # Capture a frame
   cap = cv2.VideoCapture(conf["kamera"])
   ret, frame = cap.read()
   print("[INFO] frame ret = {}".format(ret))
   logging.info("[DEBUG] frame ret = {}".format(ret))
t = TempImage()
lastpic=conf["basepath"] + "/static/lastpic.jpg"
# Save the resulting frame as a file
logging.info("[INFO] Lagrer bildet til {}".format(t.path))
cv2.imwrite(t.path, frame)
logging.info("[INFO] Lagrer bildet til {}".format(lastpic))
cv2.imwrite(lastpic, frame)
# upload the picture to the server
logging.info("[INFO] laster opp {} til {}".format(t.path, conf["host"]))
srv.put(t.path)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
# and close the SFTP
srv.close()
logging.info("[INFO] Sletter {}".format(t.path))
# and delete the picture we transfered
if os.path.exists(t.path):
  os.remove(t.path)
else:
  print("[INFO] Filen {} finnes ikke".format(t.path))
logging.info("[INFO] Ferdig")

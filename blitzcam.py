# -*-  coding: utf-8 -*-
#
#	Nye ideer:
#
#	timelaps på google-drive
#	siste timelaps-bilde med fast navn på OneDrive
#
import cv2
import argparse
import warnings
import json
import logging
import time
import datetime
import imutils
import paho.mqtt.publish as publish
import os


class TempImage:
    def __init__(self, basepath=".", ext=".jpg"):
        # construct the file path
        datestring = time.strftime("%Y%m%d-%H%M%S")
        self.path = "{base_path}/{date_String}{ext}".format(base_path=basepath,
                                                            date_String=datestring, ext=ext)

    def cleanup(self):
        # remove the file
        os.remove(self.path)


logform = '%(asctime)s %(message)s'
dateString = '%Y/%m/%d %H:%M:%S'

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

logfil = conf["logpath"]
loglevel = getattr(logging, (conf["loglevel"]).upper())
print("[INFO] Loglevel: {} til {} ".format(loglevel, logfil))
# logging.basicConfig(filename='pi_surveillance.log',level=loglevel,format='%(asctime)s %(message)s')
logging.basicConfig(filename=logfil, format=logform, datefmt=dateString, level=loglevel)

stream = conf["stream"]
logging.info("[INFO] Video from {}".format(stream))

if conf["OneDrive"]:
    logging.info("[INFO] Lagrer til OneDrive")

if conf["rotate"]:
    logging.info("[INFO] Snur bildet")

if conf["mqtt"]:
    logging.info("[INFO] Melder filnavn til MQTT")

if conf["show_video"]:
    logging.info("[INFO] Viser video på skjermen")

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
logging.info("[INFO] klargjør video...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
cap = cv2.VideoCapture(stream)

while conf["test"]:  # hvis conf test true...
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

while not (conf["test"]):  # hvis conf test false...
    # capture frames from the camera
    ret, frame = cap.read()
    # Initialize the timestamp and occupied/unoccupied text
    # grab the dimensions of the image and calculate the center
    # of the image

    # rotate the image by 180 degrees
    if conf["rotate"]:
        frame = cv2.flip(frame, conf["flip"])  # 0 = horisontalt
    #    image = frame.array
    #    (h, w) = image.shape[:2]
    #    center = (w / 2, h / 2)
    #    M = cv2.getRotationMatrix2D(center, conf["degrees"], 1.0)
    #    frame = cv2.warpAffine(image, M, (w, h))

    timestamp = datetime.datetime.now()
    text = "Stille"

    # resize the frame, convert it to grayscale, and blur it
    #    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the average frame is None, initialize it
    if avg is None:
        logging.info("[INFO] starter bildeanalyse...")
        avg = gray.copy().astype("float")
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
                           cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) > conf["min_area"]:
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Bevegelse"

    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)

    # check to see if the room is occupied
    if text == "Bevegelse":
        # check to see if enough time has passed between uploads
        if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
            # increment the motion counter
            motionCounter += 1

            # check to see if the number of frames with consistent motion is
            # high enough
            if motionCounter >= conf["min_motion_frames"]:
                # check to see if OneDrive shuld be used
                if conf["OneDrive"]:
                    # create a filename
                    t = TempImage()
                    # Build a payload for MQTT and send it
                    if conf["mqtt"]:
                        payload = [{'topic': "Motion/pic", 'payload': t.path}]
                        ret = publish.multiple(payload, hostname=conf["host"])
                    logging.info("[INFO] Oppdaget bevegelse i bildet %s, lagret som %s", ts, t.path)
                    cv2.imwrite(t.path, frame)

                # update the last uploaded timestamp and reset the motion
                # counter
                lastUploaded = timestamp
                motionCounter = 0

    # otherwise, the room is not occupied
    else:
        motionCounter = 0
        if conf["OneDrive"]:
            if conf["Tidsstyrt"] and (timestamp - lastUploaded).seconds >= conf["sekunder_mellom_bilder"]:
                # create a filename
                t = TempImage()
                # Build a payload for MQTT and send it
                if conf["mqtt"]:
                    payload = [{'topic': "Motion/pic", 'payload': t.path}]
                    ret = publish.multiple(payload, hostname=host)
                logging.info("[INFO] Tidsstyrt bilde %s, lagret som %s", ts, t.path)
                cv2.imwrite(t.path, frame)
                lastUploaded = timestamp

    # check to see if the frames should be displayed to screen
    # DISPLAY=:0
    if conf["show_video"]:
        # display the security feed
        cv2.imshow("Drivhuset", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

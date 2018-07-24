import cv2


for i in range(1, 1500):
    cap = cv2.VideoCapture(i)
    if cap.open(i):
        print "Found camera {}\n".format( i)
        break

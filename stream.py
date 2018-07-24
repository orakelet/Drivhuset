import numpy as np
import cv2
# cv2.VideoCapture('http://hello:goodbye@127.0.0.1/?action=stream?otherparamshere)
cap = cv2.VideoCapture(stream)

while(False): # settes til True
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


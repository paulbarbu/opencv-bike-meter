# inspiration for object tracking from Adrian Rosebrock:
# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

RADIUS_THRESHOLD = 5
# ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video", help="path to the (optional) video file")
# args = vars(ap.parse_args())

# define the lower and upper threshold according to the reflector's color in HSV space
# range-detector -f HSV -i bike_wheel_small.jpg -p
# range-detector is available from imutils library
REFLECTOR_LOWER_HSV = (0, 180, 0)
REFLECTOR_UPPER_HSV = (255, 255, 255)

frame = cv2.imread('bike_wheel.JPG')
frame_small = imutils.resize(frame, width=600)
blurred = cv2.GaussianBlur(frame_small, (11, 11), 0)
hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

thresholded = cv2.inRange(hsv, REFLECTOR_LOWER_HSV, REFLECTOR_UPPER_HSV)
eroded = cv2.erode(thresholded, None, iterations=2)
dilated = cv2.dilate(eroded, None, iterations=2)
contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if len(contours) > 0:
    largest_contour = max(contours, key=cv2.contourArea)
    print(largest_contour)
    ((x, y), r) = cv2.minEnclosingCircle(largest_contour)

    print('contour at center={}, radius={}'.format((x, y), r))
    if r > RADIUS_THRESHOLD:
    	# OpenCV is by default in the (B, G, R) format, so this is RED
        cv2.circle(frame_small, (int(x), int(y)), int(r), (0, 0, 255))

    	cv2.imshow('Bike-meter', imutils.resize(frame_small))

key = 0
while key != ord(' '):
    key = cv2.waitKey(0)

c2v.destroyAllWindows()
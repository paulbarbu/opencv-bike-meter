# inspiration for object tracking from Adrian Rosebrock:
# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

import argparse
import cv2
import imutils
import math

# define the lower and upper threshold according to the reflector's color in HSV space
# range-detector -f HSV -p -i reflector_in_motion.jpg
# range-detector is available from imutils library
REFLECTOR_LOWER_HSV = (15, 81, 71)
REFLECTOR_UPPER_HSV = (41, 255, 255)

# the minimum radius of the circle enclosing the found contour
# values above this will be considered as our object, and we count the rotation
# values below are noise
RADIUS_THRESHOLD = 50 # pixels

WHEEL_DIAMETER = 700 # mm
WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER/1000/1000  # km
INSTANT_FRAME_QUANTA = 120 # number of frames during which to compute the "instant" speed

# DO NOT MODIFY BELOW THIS LINE

prev_reflector = False # did we find the reflector in the previous frame?
current_reflector = False # did we find the reflector in the current frame?
rotations = 0 # number of rotations we counted up to now
frames = 0 # number of frames read up to now
time_elapsed = 0 # time in seconds since we started processing
minutes_elapsed = 0 # just another measure for time in order to display it user friendly
seconds_elapsed = 0 # just another measure for time in order to display it user friendly

instant_rotations = 0 # the number of rotations for the "instantaneous" speed computation
instant_speed = 0 # km/h
instant_distance = 0 # the distance traveled for the "instantaneous" speed computation
max_speed = 0 # km/h - max speed for the whole session

MAX_FRAME_WIDTH = 640 # pixels

parser = argparse.ArgumentParser('Process a video file or camera input in order to get the speed and distance traveled by bike on an indoor trainer')
parser.add_argument('-v', '--video', default=0, help='video file path or device number (ls /dev/ | grep video), if not passed the default camera will be used')
parser.add_argument('-f', '--fps', type=int, default=30, help='frames per second of the video or camera, it defaults to 30 if the FPS cannot be deduced from the video or to what the value of this argument is')
args = parser.parse_args()

device_or_file = args.video
try:
    device_or_file = int(args.video)
except ValueError:
    pass

video = cv2.VideoCapture(device_or_file)

if not video:
    print('Invalid video file/device')
    exit(0)

frame_rate = video.get(cv2.CAP_PROP_FPS)
if math.isnan(frame_rate):
    frame_rate = args.fps
#print('Detected frame rate: {}'.format(frame_rate))

resize = False # mark if the frame size is too large
width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
#print('Frame width: {}'.format(width))

if width > MAX_FRAME_WIDTH:
    resize = True

while video and video.isOpened():
    retval, frame = video.read()
    frames += 1

    if not retval or frame is None:
        break

    key = cv2.waitKey(1)
    if key == ord(' '):
        break

    if resize:
        # resize to reduce the time for computations
        frame_small = imutils.resize(frame, width=MAX_FRAME_WIDTH)
    else:
        frame_small = frame

    cv2.imshow('Bike-meter', frame_small)
    blurred = cv2.GaussianBlur(frame_small, (11, 11), 0) # reduce noise in the image, we don't need all the details
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # work in HSV to be able to threshold what we see

    # try to get our object of interest (the reflector) by thresholding using the pre-computed values
    thresholded = cv2.inRange(hsv, REFLECTOR_LOWER_HSV, REFLECTOR_UPPER_HSV)

    # erode and dilate to eliminate noise
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)

    # find all (external) contours
    contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # if we have at least one contour we may find one large enough to count as our object
    if len(contours) > 0:
        # only consider the biggest contour
        largest_contour = max(contours, key=cv2.contourArea)
        #print(largest_contour)
        ((x, y), r) = cv2.minEnclosingCircle(largest_contour)

        # if the radius of the enclosing circle if big enough, we just found what we need
        if r > RADIUS_THRESHOLD:
            # mark that we have found the reflector in the current frame
            current_reflector = True

            #print('contour at center={}, radius={}'.format((x, y), r))
            # OpenCV is by default in the (B, G, R) format, so this is RED
            cv2.circle(frame_small, (int(x), int(y)), int(r), (0, 0, 255))
            cv2.imshow('Bike-meter', frame_small)
        else:
            # the enclosing circle was too small, no reflector found
            current_reflector = False
            #print('No contour')
    else:
        # no contour found, no reflector found
        current_reflector = False
        #print('No contour')

    # if the reflector was not in the frame last time, but it is now, then a rotation is complete
    # this is the main assumption of this: the reflector has to
    # come into frame and get out of frame in order to properly count rotations
    if not prev_reflector and current_reflector:
        rotations += 1
        instant_rotations += 1

    # the current state becomes the previous in preparation for the next frame
    prev_reflector = current_reflector

    # this is how we keep track of time, knowing the frame rate of the captured video and how many frames we processed until now
    time_elapsed = frames/frame_rate
    distance = rotations * WHEEL_CIRCUMFERENCE # km
    avg_speed = (distance / time_elapsed) * (60*60) # km/h

    # only update the instantaneous speed once every INSTANT_FRAME_QUANTA
    if frames % INSTANT_FRAME_QUANTA == 0:
        instant_distance = instant_rotations * WHEEL_CIRCUMFERENCE # km
        instant_speed = instant_distance / (INSTANT_FRAME_QUANTA/frame_rate) * (60*60) # km/h
        instant_rotations = 0

        if instant_speed > max_speed:
            max_speed = instant_speed

    minutes_elapsed = int(time_elapsed / 60)
    seconds_elapsed = int(time_elapsed % 60)

    # \033[K - erase line contents
    # \033[F - move cursor up one line
    print('\033[Knum rotations: {:3d}; time: {:02d}:{:02d} mm:ss; avg rot/s: {:3.2f}; avg rpm: {:3.2f}; distance: {:2.2f} km; avg speed: {:2.2f} km/h'.format(rotations, minutes_elapsed, seconds_elapsed, rotations/time_elapsed, (rotations/time_elapsed)*60, distance, avg_speed))
    print('\033[Kinstant rot: {:3d}; instant distance: {:2.2f} km; instant speed: {:2.2f} km/h'.format(instant_rotations, instant_distance, instant_speed))
    print('\033[Kmax speed: {:2.2f} km/h'.format(max_speed))
    print('\033[F\033[F\033[F\033[F') # move up 4 lines so that next time I overwrite what I just displayed

#print('time_elapsed: {}'.format(time_elapsed))
if video and time_elapsed > 0:
    print('\033[Knum rotations: {:3d}; time: {:02d}:{:02d} mm:ss; avg rot/s: {:3.2f}; avg rpm: {:3.2f}; distance: {:2.2f} km; avg speed: {:2.2f} km/h'.format(rotations, minutes_elapsed, seconds_elapsed, rotations/time_elapsed, (rotations/time_elapsed)*60, distance, avg_speed))
    print('\033[Kinstant rot: {:3d}; instant distance: {:2.2f} km; instant speed: {:2.2f} km/h'.format(instant_rotations, instant_distance, instant_speed))
    print('\033[Kmax speed: {:2.2f} km/h'.format(max_speed))
else:
    print('video might not have been opened')

video.release()
cv2.destroyAllWindows()

Bike-Meter
==========
A simple speed and distance bike computer built using OpenCV and Python 3.

If you're using your bike on a home trainer and don't have the necessary speed sensors on it, this might help.
It uses OpenCV to count your back wheel's rotations and from there it computes the speed and distance
traveled for the current training session.

So you need to place your laptop/RPi/webcam beside the back wheel and to have a reflective or coloured sticker or safety element on the wheel.
Anything that spins with the wheel and is a bit different from it and the background should work.
Aim your camera only at a part of the wheel, so that the sticker/reflector gets in and out of frame. this is the working principle of this application. Whenever the sticker appears in frame try to detect it and I count a rotation. Knowing the size of the wheel I can compute the distance traveled. Keeping track of the time elapsed speed can be computed as well.

*NOTE:* Make sure nothing will get stuck to your wheel, cables and such. Do not damage your equipment or yourself.

Also note that the results and performance of this program may vary with lightning conditions, camera quality (although I have used a crappy one and it worked), object size, color and positioning.
See the example picture and video in this repository for demo.

Usage
=====
Install the required packages:
`pip install -r requirements.txt`

Configure your threshold levels, place the reflective element in front of the camera and capture an image or a video (then choose one of the frames of the video), then:

`range-detector -f HSV -p -i reflector_in_motion.jpg`

After you've isolated the reflective/coloured element from your wheel, plug the numbers in
the `REFLECTOR_LOWER_HSV` and `REFLECTOR_UPPER_HSV` variables in the code.

Also you may need to change the `WHEEL_DIAMETER` to reflect you wheel's diameter in millimeters for accurate computations.

Finally you may need to tweak `RADIUS_THRESHOLD` to an appropriate number for your object,
camera and distance.
If no rotation or too many rotations are detected, you need to increase or decrease this number (it's in pixels).

Run, either with a live camera (`ls /dev/ | grep video` and get the number):
`python bike-meter.py -v 2`

Or with a pre-recorded video:
`python bike-meter.py -v v1.mp4`

LICENSE
=======
Copyright 2020 Barbu Paul - Gheorghe

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

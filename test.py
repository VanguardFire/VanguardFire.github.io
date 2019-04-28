from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import time
import cv2
import json
import imutils
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

conf = json.load(open("/home/pi/Desktop/conf.json"))

# In[4]:


camera = PiCamera()
#camera.sensor_mode = 7
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
camera.iso = 100
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])

camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
#g = camera.awb_gains
#camera.awb_mode = 'off'
#camera.awb_gains = g

count = 0
centerX = 160
centerY = 120



def process(gray):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7),0)
    
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations =4)
    return edged

def process2(gray):
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    gray = cv2.inRange(gray, (0.0, 0.0, 74.9),  (180, 250, 255))
    return cv2.dilate(gray, None, iterations =4)
    


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
    #count = count + 1
    image = frame.array
    contourAvail = False 
    #resize the frame, convert it to grayscale, and blur it
    #frame = imutils.resize(frame, width=500)
    
    cnts = cv2.findContours(process2(image).copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
 
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < conf["min_area"]:
            continue
        if cv2.contourArea(c) > conf["max_area"]:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        centerX = x + (w/2)
        centerY = y + (h/2)
        fireLocationToString = "(" + str(centerX) + ", " + str(centerY) + ")"
        print (fireLocationToString)
        contourAvail = True
        
    
    if contourAvail == True:
        if(centerY > 120):
            kit.stepper1.onestep(style = stepper.DOUBLE, direction = stepper.BACKWARD)
        if(centerY <120):
           kit.stepper1.onestep(style = stepper.DOUBLE)
        

    cv2.imshow("test", image)
    
    key = cv2.waitKey(1) & 0xFF
 
    if key == ord("q"):
        break
    
    
        
    
    #print(count)
    
    rawCapture.truncate(0)
    
camera.close()
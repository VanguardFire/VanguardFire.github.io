# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:16:18 2019

@author: Ivan
"""

from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2
import json

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()


counter = 0
centerX = 160
centerY = 120

homeX = 0
homeY = 0

xDirec = True
yDirec = True

conf = json.load(open("/home/pi/Desktop/conf.json"))
vs = PiVideoStream().start()
time.sleep(2.0)
contourAvail = False


def process(gray):
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7),0)
    
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations =4)
    return edged

def process2(gray):
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    gray = cv2.inRange(gray, (0.0, 0.0, 74.9),  (180, 250, 255))
    return cv2.dilate(gray, None, iterations =4)


while True:
    counter = counter +1
    print(counter)
    
    frame = vs.read()
    cv2.imshow("frame", frame)
    
    cnts = cv2.findContours(process2(frame).copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    contourAvail = False
    
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
        location = (centerX, centerY)
        print ((centerX, centerY))
        contourAvail = True
    
    
    if contourAvail == False:
        if homeX > 1200 :
            xDirec = True
        if homeX < 0:
            xDirec = False
    
        
        if xDirec == True:
            kit.stepper1.onestep(style = stepper.DOUBLE)
            homeX = homeX -1
        if xDirec == False:
            kit.stepper1.onestep(style = stepper.DOUBLE, direction = stepper.BACKWARD)
            homeX = homeX+1
            
        if homeY > 100:
            yDirec = True
        
        if homeY < 0:
            yDirec = False
    
        
        if yDirec == True:
            kit.stepper2.onestep(style = stepper.DOUBLE, direction = stepper.BACKWARD)
            homeY = homeY -1
        if yDirec == False:
            kit.stepper2.onestep(style = stepper.DOUBLE)
            homeY = homeY+1
    
    if contourAvail == True:
        if centerX < 158:
            kit.stepper1.onestep(style = stepper.DOUBLE)
            homeX = homeX-1
        if centerX > 162:
            kit.stepper1.onestep(style = stepper.DOUBLE, direction = stepper.BACKWARD)
            homeX = homeX+1
            
        if centerY < 117 and counter % 2 == 0:
            kit.stepper2.onestep(style = stepper.DOUBLE, direction = stepper.BACKWARD)
            homeY = homeY -1
        if centerY > 123 and counter % 2 == 0:
            kit.stepper2.onestep(style = stepper.DOUBLE)
            homeY = homeY+1
        
    
            
            
        
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
vs.stop()
kit.stepper1.release()
kit.stepper2.release()



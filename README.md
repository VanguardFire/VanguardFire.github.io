# VanguardFire.github.io



<iframe src="https://drive.google.com/file/d/1y6lS_Jfq6A3C09uoXLYb2u_boHbMYpje/preview" width="1000" height="700"></iframe>

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRvvz6JIVjFyv-IuHR6Xv3hYkoH6HtR1ViAjw_LoqJzr33nBfokJ3LRL47SqkbgreVing1hrMc1826y/embed?start=false&loop=true&delayms=5000" frameborder="0" width="960" height="569" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>



#Our Code and Some Results:


from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import datetime
import time
import cv2
import json
import imutils


conf = json.load(open("/home/pi/Desktop/conf.json"))





camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))





print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0





#capture frames from the camera
count = 0

for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    
    
    
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "You're good"
    
    
 
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
  
        
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21),0)
    
    if count ==0:
        firstFrame = gray
 

    # if the average frame is None, initialize it
    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    #cv2.accumulateWeighted(gray, avg, 0.5)
    #frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    
    frameDelta = cv2.absdiff(gray, firstFrame)
    
    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=10)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
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
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Ain't nobody got time for dat"
        
        centerX = x + (w/2)
        centerY = y + (h/2)
        fireLocation = (centerX, centerY)
        fireLocationToString = "(" + str(centerX) + ", " + str(centerY) + ")"
        
        cv2.putText(frame, "Fire Location: {}".format(fireLocationToString), (10,40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Fire Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.35, (0, 0, 255), 1)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
            break
    
    # check to see if the frames should be displayed to screen
    if conf["show_video"]:
        # display the security feed
        cv2.imshow("Security Feed", frame)
        #cv2.imshow("Change", frameDelta)
        cv2.imshow("Thresh", thresh)
        #cv2.imshow("First Frame", firstFrame)
        key = cv2.waitKey(1) & 0xFF
 
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    count = count +1

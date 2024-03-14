import numpy as np
import cv2
from picamera2 import Picamera2
from libcamera import controls
import time
import RPi.GPIO as GPIO

GPIO.cleanup()
picam2 = Picamera2() # assigns camera variable
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous}) # sets auto focus mode
picam2.start() # activates camera

time.sleep(1) # wait to give camera time to start up

# GPIO pins setup
OUT1 = 17 # right motor
OUT2 = 27 # right motor
OUT3 = 23 # left motor
OUT4 = 24 # left motor
ENA = 22 # right PWM
ENB = 25 # left PWM

GPIO.setmode(GPIO.BCM)
GPIO.setup(OUT1, GPIO.OUT)
GPIO.setup(OUT2, GPIO.OUT)
GPIO.setup(OUT3, GPIO.OUT)
GPIO.setup(OUT4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

GPIO.output(OUT1,GPIO.LOW)
GPIO.output(OUT2,GPIO.LOW)
GPIO.output(OUT3,GPIO.LOW)
GPIO.output(OUT4,GPIO.LOW)

# parameters
hz = 40 # [Hz] frequency for pwm pins
runtime = 0.1 # [s] execution time for each steer
pwm0 = 50 # base motor pwms

kp = 0.5 # proportional control constant
ki = 0.05 # integral control constant
kd = 0.25 # derivative control constant

mid_low = 280 
mid_up = 360
desired = (mid_low+mid_up)/2

pwm_right = GPIO.PWM(ENA, hz) # right motor PWM setup
pwm_left = GPIO.PWM(ENB, hz) # left motor PWM setup

def straight():
    global pwm0, runtime # to reference runtime and pwm0
    pwm_left.ChangeDutyCycle(pwm0)
    pwm_right.ChangeDutyCycle(pwm0)
    # print("STRAIGHT")
    time.sleep(runtime)
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    
def left(pwm):
    global pwm0, runtime
    pwm_left.ChangeDutyCycle(pwm0+pwm) # left pwm lower to turn left (pwm is negative)
    pwm_right.ChangeDutyCycle(pwm0-pwm)
    # print("LEFT")
    time.sleep(runtime)
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    
def right(pwm):
    global pwm0, runtime
    pwm_left.ChangeDutyCycle(pwm0+pwm)
    pwm_right.ChangeDutyCycle(pwm0-pwm) # right pwm lower to turn right
    # print("RIGHT")
    time.sleep(runtime)
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    
def error(current):
    global desired
    
    err = desired - current
    # positive error: left of line turn right)
    # negative error: right of line (turn left)
    
    print("error: {}".format(str(err)))
    return err
    
def pid(error_arr):
    global kp,ki,kd
    
    p = error_arr[-1] * kp
    # i = sum(error_arr) * ki
    # d = (error_arr[-1]-error_arr[-2]) * kd
    
    PID = p
    if PID >= 50:
        PID = 50
    if PID <= -50:
        PID = -50
    # PID = p+i+d
    print("PID: {}".format(str(PID)))
    return PID
   
try:

    # starting PWM
    pwm_left.start(0) # value 0-100 controls speed of left motor
    pwm_right.start(0) # value 0-100 controls speed of left motor
    # setting pins high
    GPIO.output(OUT1, GPIO.HIGH) # starts right motor
    GPIO.output(OUT3, GPIO.HIGH) # starts left motor

    while True:
        # Display camera input
        image = picam2.capture_array("main")
        cv2.imshow('img',image)
    
        # Crop the image
        # crop_img = image[60:120, 0:160] # brianna's
        crop_img = image
        # original_height, original_width, _ = crop_img.shape
        # print("original image dimensions: {} x {}".format(original_width, original_height))
    
        # Convert to grayscale
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    
        # Gaussian blur
        blur = cv2.GaussianBlur(gray,(5,5),0)
    
        # Color thresholding
        input_threshold,comp_threshold = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
    
        # Find the contours of the frame
        contours,hierarchy = cv2.findContours(comp_threshold.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
        # Find the biggest contour (if detected)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c) # determine moment - weighted average of intensities

            if int(M['m00']) != 0:
                cx = int(M['m10']/M['m00']) # find x component of centroid location
                cy = int(M['m01']/M['m00']) # find y component of centroid location
            else:
                print("Centroid calculation error, looping to acquire new values")
                continue
            cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1) # display vertical line at x value of centroid
            cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1) # display horizontal line at y value of centroid
    
            cv2.drawContours(crop_img, contours, -1, (0,255,0), 2) # display green lines for all contours
            
            # determine location of centroid in x direction and adjust steering recommendation
            
            errors = [0,0]
            err = error(cx)
            errors.append(err)
            new_pwm = pid(errors)
            
            if cx >= mid_up:
                print("Turn left")
                left(new_pwm)
    
            if cx < mid_up and cx > mid_low:
                print("On Track")
                straight()
    
            if cx <= mid_low:
                print("Turn Right")
                right(new_pwm)
    
        else:
            print("I don't see the line")
    
        # Display the resulting frame
        cv2.imshow('frame',crop_img)
        
        # Show image for x ms then continue to next image
        cv2.waitKey(100) # [ms]

# exception for errors

except KeyboardInterrupt:
    print('All done')
    GPIO.cleanup()

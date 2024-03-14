import RPi.GPIO as GPIO
import time

# Assign GPIO pin numbers to variables
s2 = 0
s3 = 5
sig = 6 #labeled "out" on your board
cycles = 10

def DetectColor():
    # Detect red values
    GPIO.output(s2, GPIO.LOW)
    GPIO.output(s3, GPIO.LOW)
    time.sleep(0.001)
    start_time = time.time()
    for count in range(cycles):
        GPIO.wait_for_edge(sig, GPIO.FALLING)
    duration = time.time() - start_time
    red = cycles / duration
    # print("red value - ", red)

    # Detect green values
    GPIO.output(s2, GPIO.HIGH)
    GPIO.output(s3, GPIO.HIGH)
    time.sleep(0.001)
    start_time = time.time()
    for count in range(cycles):
        GPIO.wait_for_edge(sig, GPIO.FALLING)
    duration = time.time() - start_time
    green = cycles / duration
    # print("green value - ", green)

    # Detect blue values
    GPIO.output(s2, GPIO.LOW)
    GPIO.output(s3, GPIO.HIGH)
    time.sleep(0.001)
    start_time = time.time()
    for count in range(cycles):
        GPIO.wait_for_edge(sig, GPIO.FALLING)
    duration = time.time() - start_time
    blue = cycles / duration
    # print("blue value - ", blue)

    return red, green, blue

# motor and pwm pins
motor_pin1 = 17
motor_pin2 = 27
motor_pin3 = 23
motor_pin4 = 24
ena = 22
enb = 25

# pid constants and control
kp = 1.0
ki = 0.05
kd = 1.0
setpoint = (25500,26000,24500)

# Setup GPIO and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(s2, GPIO.OUT)
GPIO.setup(s3, GPIO.OUT)
GPIO.setup(sig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(motor_pin1, GPIO.OUT)
GPIO.setup(motor_pin2, GPIO.OUT)
GPIO.setup(motor_pin3, GPIO.OUT)
GPIO.setup(motor_pin4, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)

GPIO.output(motor_pin1, GPIO.LOW)
GPIO.output(motor_pin2, GPIO.LOW)
GPIO.output(motor_pin3, GPIO.LOW)
GPIO.output(motor_pin4, GPIO.LOW)
GPIO.setup(ena, GPIO.LOW)
GPIO.setup(enb, GPIO.LOW)

freq = 500
pwm0 = 40
pwm_L = GPIO.PWM(ena, freq)
pwm_R = GPIO.PWM(enb, freq)

def straight(pwm, runtime):
    print("STRAIGHT")
    GPIO.output(motor_pin1, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.LOW)
    pwm_L.ChangeDutyCycle(pwm)
    pwm_R.ChangeDutyCycle(pwm)
    pwm_L.start(pwm)
    pwm_R.start(pwm)
    time.sleep(runtime)

def right(left_pwm, runtime):
    print("RIGHT")
    GPIO.output(motor_pin1, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.LOW)
    pwm_L.ChangeDutyCycle(left_pwm)
    pwm_R.ChangeDutyCycle(left_pwm*0.6)
    pwm_L.start(left_pwm)
    pwm_R.start(left_pwm*0.6)
    time.sleep(runtime)

def left(right_pwm, runtime):
    print("LEFT")
    GPIO.output(motor_pin1, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.LOW)
    pwm_L.ChangeDutyCycle(right_pwm*0.6)
    pwm_R.ChangeDutyCycle(right_pwm)
    pwm_L.start(right_pwm*0.6)
    pwm_R.start(right_pwm)
    time.sleep(runtime)

def stop():
    print("STOP")
    GPIO.output(motor_pin1, GPIO.LOW)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.LOW)
    GPIO.output(motor_pin4, GPIO.LOW)
    pwm_L.start(0)
    pwm_R.start(0)

def get_color(red, green, blue):
    if red >= 22000 and red <= 39000 and blue >= 21000 and blue <= 26000 and green >= 18000 and green <= 38000:
        return "white"
    
    elif max(red,blue,green) == red:
        return "red"
    elif red >= 19000 and red <= 22000 and blue >= 24000 and blue <= 27000 and green >= 16500 and green <= 20000:
        return "purple"
    else: 
        return "not either"

t = 0.15

def follow_line():
    try:
        while True:
            r0,g0,b0 = DetectColor()
            color = get_color(r0,g0,b0)

            if color == "white":
                left(pwm0, t)
            
            elif color == "red":
                right(pwm0, t)
            
            elif color == "purple":
                right(pwm0, t)
        
            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()

try:

    follow_line()
    time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
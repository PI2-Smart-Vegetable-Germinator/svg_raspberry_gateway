import RPi.GPIO as GPIO
import time

illumination = 12
irrigation = 16
irrigation_time = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(illumination, GPIO.OUT)
GPIO.setup(irrigation, GPIO.OUT)

def switch_illumination ():
    if(GPIO.input(illumination) == 0):
        GPIO.output(illumination, 1)
    else:
        GPIO.output(illumination, 0)

def start_irrigation():
    GPIO.output(irrigation, 1)

def end_irrigation():
    GPIO.output(irrigation, 0)
    

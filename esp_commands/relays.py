import RPi.GPIO as GPIO
import time

illumination = 12
irrigation = 16
irrigation_time = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(illumination, GPIO.OUT)
GPIO.setup(irrigation, GPIO.OUT)

def get_illumination_state():
    # return GPIO.input(illumination)
    return 1

def switch_illumination ():
    if(get_illumination_state() == 0):
        GPIO.output(illumination, 1)
    else:
        GPIO.output(illumination, 0)

    return get_illumination_state()

def start_irrigation():
    GPIO.output(irrigation, 1)

def end_irrigation():
    GPIO.output(irrigation, 0)
    

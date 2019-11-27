#import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os, json, requests
from requests.exceptions import RequestException

from project import socketio

illumination = 12
irrigation = 16
irrigation_time = 10

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(illumination, GPIO.OUT)
# GPIO.setup(irrigation, GPIO.OUT)

def get_illumination_state():
    # return GPIO.input(illumination)
    return 0

def switch_illumination ():
    if(get_illumination_state() == 0):
        # GPIO.output(illumination, 1)
        print('acionar iluminação')
        return 1
    else:
        # GPIO.output(illumination, 0)
        print('desligar iluminação')
        return 0


    return get_illumination_state()

def start_irrigation():
    data = {}
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    try:
        response = requests.post('%s/api/start_irrigation' %
                                 os.getenv('EXTERNAL_GATEWAY_URL'), json=data)
    except RequestException as e:
        print(str(e))

    #GPIO.output(irrigation, 1)
    print('irrigar')
    time.sleep(irrigation_time)
    #GPIO.output(irrigation, 0)

    socketio.emit('irrigationFinished', {'success': True})

    machine_info['latestIrrigation'] = str(datetime.now())

    with open(os.path.dirname(__file__) + '/../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    try:
        response = requests.post('%s/api/end_irrigation' %
                                 os.getenv('EXTERNAL_GATEWAY_URL'), json={"plantingId" : machine_info.get('plantingId')})
    except RequestException as e:
        print(str(e))
    
    

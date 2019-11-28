#!/usr/bin/env python 3
import serial
import time
import json
import esp_commands.relays as relays
from datetime import datetime
import os
from datetime import timedelta


def get_sensor_data():
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3) #substituindo ttyACM0 pelo USB da ESP32
    except serial.SerialException as e:
        print("deu ruim")
        print(str(e))
        return {}

    comunicacaoSerial.write(b'sensores')
    
    time.sleep(1)

    s = comunicacaoSerial.readline().decode('UTF-8')

    while '{' not in s:
        print(s)
        s = comunicacaoSerial.readline().decode('UTF-8')


    s += comunicacaoSerial.readline().decode('UTF-8')
    s += comunicacaoSerial.readline().decode('UTF-8')
    s += comunicacaoSerial.readline().decode('UTF-8')
    s += comunicacaoSerial.readline().decode('UTF-8')
    s += comunicacaoSerial.readline().decode('UTF-8')

    j = json.loads(s)
    j['currentBacklit'] = relays.get_illumination_state()
    return j

def check_illumination(illumination):

    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

    if not machine_info.get('illuminationTime'):
        machine_info['illuminationTime'] = 0

    if illumination is not None and illumination > 2000 and machine_info.get('illuminated'):
        last_updated = machine_info.get('lastUpdated')
        if not last_updated:
            last_updated = str(datetime.now())
        delta = datetime.now() - datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        
        if not machine_info.get('illuminationTime'):
            machine_info['illuminationTime'] = delta.seconds
        else:
            machine_info['illuminationTime'] = int(machine_info['illuminationTime']) + delta.seconds
        
        with open(os.path.dirname(__file__) + '/../assets/machine_info.json', 'w') as json_file:
            json.dump(machine_info, json_file)
    elif illumination is not None and illumination > 2000:
        machine_info['illuminated'] = True
        with open(os.path.dirname(__file__) + '/../assets/machine_info.json', 'w') as json_file:
            json.dump(machine_info, json_file)
    else:
        machine_info['illuminated'] = False
        with open(os.path.dirname(__file__) + '/../assets/machine_info.json', 'w') as json_file:
            json.dump(machine_info, json_file)
    
    timestring = str(timedelta(seconds=machine_info['illuminationTime']))
    timestring_tokens = timestring.split(':')
    formatted_timestring = "%sh %sm" % (timestring_tokens[0], timestring_tokens[1])
    return formatted_timestring

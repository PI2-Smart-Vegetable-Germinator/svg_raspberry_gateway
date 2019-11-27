#!/usr/bin/env python 3
import serial
import time
import json
import esp_commands.relays as relays


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
    j['currently_backlit'] = relays.get_illumination_state()
    print(j)
    return j


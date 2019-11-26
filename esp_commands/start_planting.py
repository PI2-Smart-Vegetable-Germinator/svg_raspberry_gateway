import serial
import sys
import time

from project import socketio

def activate_planting():
    
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3) #substituindo ttyACM0 pelo USB da ESP32
    except serial.SerialException as e:
        print('deu ruim')
        print(str(e))
        return

    comunicacaoSerial.write(b'plantar')

    comunicacaoSerial.close()

def stop_planting():
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3)
    except serial.SerialException as e:
        print(str(e))
        return
    
    comunicacaoSerial.write(b'cancela')

    comunicacaoSerial.close()

def monitor_planting_progress():
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3)
    except serial.SerialException as e:
        print(str(e))
        return

    while True:
        time.sleep(1)
        line = comunicacaoSerial.readline().decode('utf-8')
        print('oi to na thread')

        if "falsapresenca" in line:
            print('oi deu erro na thread devia emitir agora')
            socketio.emit('erroPresenca', {'success': False})
            comunicacaoSerial.close()
            break
        elif "fimdecurso" in line:
            socketio.emit('plantingSuccess', {'success': True})
            comunicacaoSerial.close()
            break

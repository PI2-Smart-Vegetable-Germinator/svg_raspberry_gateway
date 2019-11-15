import serial
import sys

def activate_planting():
    
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3) #substituindo ttyACM0 pelo USB da ESP32
    except serial.SerialException as e:
        print('deu ruim')
        print(str(e))
        return

    comunicacaoSerial.write(b'plantar')

    a = comunicacaoSerial.readline().decode('utf-8')
    print(a)

    comunicacaoSerial.close()

def stop_planting():
    try:
        comunicacaoSerial = serial.Serial('/dev/ttyUSB0', 9600, timeout=3)
    except serial.SerialException as e:
        print(str(e))
        return
    
    comunicacaoSerial.write(b'cancelar')

    comunicacaoSerial.close()

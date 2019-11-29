import urllib
import requests
import os
import json

from esp_commands.sensor_data import get_sensor_data


def check_connection():
    try:
        urllib.request.urlopen('http://google.com', timeout=5)
    except urllib.error.URLError as err:
        return False

    return True


def refresh_data():
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

    if machine_info.get('finishedCycles'):
        for planting_id in machine_info.get('finishedCycles'):
            requests.post('%s/api/end_planting' %
                            os.getenv('EXTERNAL_GATEWAY_URL'), json={'plantingId': planting_id}, timeout=8)
        machine_info['finishedCycles'] = []

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    if machine_info.get('plantingActive') and not machine_info.get('plantingId'):
        seedling_id = machine_info.get('seedlingId')
        requests.post('http://localhost:5005/api/confirm_planting', json={'seedlingId': seedling_id}, timeout=8)
    elif machine_info.get('plantingActive') and machine_info.get('plantingId'):
        sensor_info = get_sensor_data()
        data = {
            'currentTemperature': sensor_info.get('TemperaturaAr'),
            'currentHumidity': sensor_info.get('UmidadeSolo'),
            'currentAirHumidity': sensor_info.get('UmidadeAr')
        }

        requests.post('http://localhost:5005/update_info', json=data, timeout=8)

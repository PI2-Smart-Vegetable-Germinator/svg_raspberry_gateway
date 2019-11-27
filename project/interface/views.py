import subprocess
from esp_commands.start_planting import stop_planting
from esp_commands.start_planting import monitor_planting_progress
from esp_commands.start_planting import activate_planting
import time
from threading import Thread
import serial
from esp_commands.sensor_data import get_sensor_data
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import requests
from requests.exceptions import RequestException
import os
import json
from wifi import Cell, Scheme

from .utils import check_connection
from .utils import refresh_data
from project import socketio

import esp_commands.relays as relays

from random import randrange

interface_blueprint = Blueprint("interface", __name__)


@interface_blueprint.route('/api/ping')
def ping():
    return jsonify({'response': 'pong!'}), 200

@interface_blueprint.route('/app/start')
def start_system():
    return render_template('start_screen.html')


@interface_blueprint.route('/app/pairing')
def pair_device():
    pin = randrange(9999)
    data = {'pincode': ('%04d' % pin)}
    plantingActive = None
    plantingId = None

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)
        plantingActive = machine_info.get('plantingActive')
        plantingId = machine_info.get('plantingId')

        if machine_info.get('id'):
            data['id'] = machine_info.get('id')

    response = requests.post('%s/api/machine' %
                             os.getenv('EXTERNAL_GATEWAY_URL'), json=data)

    print("\n\n=============")
    print(response.url)
    print("=============\n\n")

    if response.json().get('machineId'):
        with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
            existing_info = {}
            existing_info['plantingActive'] = plantingActive
            existing_info['plantingId'] = plantingId
            existing_info['id'] = response.json()['machineId']
            json.dump(existing_info, json_file)

    return render_template('pairing.html', pin=('%04d' % pin))


@interface_blueprint.route('/app/home')
def home():
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'r+') as json_file:
        machine_info = json.load(json_file)

        has_wifi = check_connection()

        if not machine_info.get('id'):
            if has_wifi:
                return redirect('pairing')
            return redirect('wifi')

        if not machine_info.get('plantingActive'):
            seedlings_file = open(os.path.dirname(
                __file__) + '/../../assets/seedlings.json')
            seedlings_data = json.load(seedlings_file)
            seedlings_file.close()
            return render_template('planting.html', seedlings=seedlings_data['seedlings'], hasWifi=has_wifi)

        sensor_info = get_sensor_data()
        data = {
            'currentTemperature': sensor_info.get('TemperaturaAr'),
            'currentHumidity': sensor_info.get('UmidadeSolo'),
            'currentAirHumidity': sensor_info.get('UmidadeAr'),
            'hasWifi': has_wifi
            # Luximetro
        }

        return render_template('home.html', data=data)



@interface_blueprint.route('/api/confirm_pairing')
def confirm_pairing():
    socketio.emit('device_paired', {'success': True})
    return jsonify({'success': True}), 200


# SECTION IRRIGATION --------------------------------------------------

@interface_blueprint.route('/api/start_irrigation')
def start_irrigation():
    data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    try:
        response = requests.post('%s/api/start_irrigation' %
                                 os.getenv('EXTERNAL_GATEWAY_URL'), json=data)
    except RequestException as e:
        print(str(e))

    return jsonify({'success': True}), 200


@interface_blueprint.route('/api/app/start_irrigation')
def app_start_irrigation():

    return jsonify({'success': True, 'app_start_irrigation': 'testinho-top'}), 200


@interface_blueprint.route('/api/end_irrigation')
def end_irrigation():
    data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    try:
        response = requests.post('%s/api/end_irrigation' %
                                os.getenv('EXTERNAL_GATEWAY_URL'), json=data)
    except RequestException as e:
        print(str(e))

    return jsonify({'success': True}), 200


@interface_blueprint.route('/api/app/end_irrigation')
def app_end_irrigation():

    return jsonify({'success': True, 'app_end_irrigation': 'testinho-fim'}), 200


# SECTION ILLUMINATION --------------------------------------------------

@interface_blueprint.route('/api/switch_illumination')
def switch_illumination():
    data = {}
    state = relays.switch_illumination()

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    if state:
        data['currently_backlit'] = "True"
    else:
        data['currently_backlit'] = "False"

    try:
        response = requests.post('%s/api/switch_illumination' %
                                os.getenv('EXTERNAL_GATEWAY_URL'), json=data)
    except RequestException as e:
        print(str(e))

    return jsonify(response.json()), response.status_code


@interface_blueprint.route('/api/app/switch_illumination')
def app_switch_illumination():
    data = {}
    state = relays.switch_illumination()

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    if state:
        return jsonify({'success': True, 'currently_backlit': True}), 200
    else:
        return jsonify({'success': True, 'currently_backlit': False}), 200


# SECTION PLANTING --------------------------------------------------


@interface_blueprint.route('/api/start_planting', methods=['POST'])
def start_planting():
    activate_planting()
    t = Thread(target=monitor_planting_progress)
    t.start()
    return jsonify({'success': True}), 201


@interface_blueprint.route('/api/confirm_planting', methods=['POST'])
def confirm_planting():
    post_data = request.get_json()
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        post_data['machineId'] = machine_info.get('id')

    sensor_info = get_sensor_data()

    post_data['currentTemperature'] = sensor_info.get('TemperaturaAr')
    post_data['currentHumidity'] = sensor_info.get('UmidadeSolo')
    post_data['currentAirHumidity'] = sensor_info.get('UmidadeAr')

    try:
        response = requests.post('%s/api/start_planting' %
                                os.getenv('EXTERNAL_GATEWAY_URL'), json=post_data)

        response_json = response.json()
        machine_info['plantingActive'] = True
        machine_info['seedlingId'] = post_data['seedlingId']
        machine_info['plantingId'] = response_json.get('plantingId')
    except RequestException:
        machine_info['plantingActive'] = True
        machine_info['seedlingId'] = post_data['seedlingId']
        machine_info['plantingId'] = None


    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    return jsonify({'success': True}), 201


@interface_blueprint.route('/api/cancel_planting')
def cancel_planting():
    stop_planting()
    return jsonify({'success': True}), 201


@interface_blueprint.route('/api/end_planting')
def end_planting():
    post_data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        post_data['plantingId'] = machine_info.get('plantingId')

    try:
        response = requests.post('%s/api/end_planting' %
                                os.getenv('EXTERNAL_GATEWAY_URL'), json=post_data)
        machine_info['plantingActive'] = False
        machine_info['plantingId'] = None
    except RequestException:
        machine_info['plantingActive'] = False
        if not machine_info.get('finishedCycles'):
            machine_info['finishedCycles'] = [machine_info.get('plantingId')]
        else:
            machine_info['finishedCycles'].append(machine_info.get('plantingId'))
        machine_info['plantingId'] = None

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    return jsonify({'success': True}), 201


@interface_blueprint.route('/app/wifi', methods=['GET', 'POST'])
def see_networks():
    error = False
    cells = []
    while not cells:
        cells = Cell.all('wlan0')

    networks = []
    for c in cells:
        networks.append(c.ssid)

    return render_template('wifi.html', networks=networks, error=error, form=None)


@interface_blueprint.route('/api/connect', methods=['POST'])
def connect_to_wifi():
    post_data = request.get_json()
    print(post_data)

    base_path = os.path.dirname(__file__)

    connect_path = base_path + "/wifi-connection.sh"

    print(post_data['password'])
    print(post_data['ssid'])

    subprocess.call([connect_path, post_data['password'], post_data['ssid']])

    for i in range(0, 4):
        time.sleep(5)
        if check_connection():
            refresh_data()
            return jsonify({
                'success': True
            }), 201

    reset_path = base_path + "/reset-wpa.sh"
    subprocess.call([reset_path])

    return jsonify({
        'success': False
    }), 400


@interface_blueprint.route('/app/key')
def keyboard():
    return render_template('keyboard.html')

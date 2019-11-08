from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

import requests, os, json

from project import socketio

from random import randrange

interface_blueprint = Blueprint("interface", __name__)

@interface_blueprint.route('/app/start')
def start_system():
    machine_id = None
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        if machine_info.get('id'):
            machine_id = machine_info.get('id')
    return render_template('start_screen.html', hasId=(machine_id != None))

@interface_blueprint.route('/app/pairing')
def pair_device():
    pin = randrange(9999)
    data = {'pincode' : ('%04d' % pin)}

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        if machine_info.get('id'):
            data['id'] = machine_info.get('id')

    response = requests.post('%s/api/machine' % os.getenv('EXTERNAL_GATEWAY_URL'), json=data)

    if response.json().get('machineId'):
        with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
            existing_info = json.load(json_file)
            existing_info['id'] = response.json()['machineId']
            json.dump(existing_info, json_file)

    return render_template('pairing.html', pin=('%04d' % pin))

@interface_blueprint.route('/app/home')
def home():
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        if not machine_info.get('plantingActive'):
            seedlings_file = open(os.path.dirname(__file__) + '/../../assets/seedlings.json')
            seedlings_data = json.load(seedlings_file)
            seedlings_file.close()
            return render_template('planting.html', seedlings=seedlings_data['seedlings'])
    return render_template('home.html')

@interface_blueprint.route('/api/confirm_pairing')
def confirm_pairing():
    socketio.emit('device_paired', {'success': True})
    return jsonify({'success': True}), 200

@interface_blueprint.route('/api/start_irrigation')
def start_irrigation():
    data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    response = requests.post('%s/api/start_irrigation' % os.getenv('EXTERNAL_GATEWAY_URL'), json=data)

    return jsonify({'success': True}), 200

@interface_blueprint.route('/api/end_irrigation')
def end_irrigation():
    data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        data['plantingId'] = machine_info.get('plantingId')

    response = requests.post('%s/api/end_irrigation' % os.getenv('EXTERNAL_GATEWAY_URL'), json=data)

    return jsonify({'success': True}), 200

@interface_blueprint.route('/api/start_planting', methods=['POST'])
def start_planting():
    post_data = request.get_json()
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        post_data['machineId'] = machine_info.get('id')

    with open(os.path.dirname(__file__) + '/../../test_data.json') as json_file:
        sensor_info = json.load(json_file)
        post_data['currentTemperature'] =  sensor_info['temperature']
        post_data['currentHumidity'] = sensor_info['humidity']

    response = requests.post('%s/api/start_planting' % os.getenv('EXTERNAL_GATEWAY_URL'), json=post_data)

    response_json = response.json()
    machine_info['plantingActive'] = True
    machine_info['plantingId'] = response_json.get('plantingId')

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    return jsonify({'success': True}), 201

@interface_blueprint.route('/api/end_planting')
def end_planting():
    post_data = {}
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        post_data['plantingId'] = machine_info.get('plantingId')

    response = requests.post('%s/api/end_planting' % os.getenv('EXTERNAL_GATEWAY_URL'), json=post_data)
    machine_info['plantingActive'] = False
    machine_info['plantingId'] = None

    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)

    return jsonify({'success': True}), 201

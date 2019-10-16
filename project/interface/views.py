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
    return render_template('start_screen.html')

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
            json.dump({'id' : response.json()['machineId']}, json_file)

    return render_template('pairing.html', pin=('%04d' % pin))

@interface_blueprint.route('/app/home')
def home():
    return render_template('home.html')

@interface_blueprint.route('/api/confirm_pairing')
def confirm_pairing():
    socketio.emit('device_paired', {'success': True})
    return jsonify({'success': True}), 200
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

import requests, os, json
from wifi import Cell, Scheme

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
            json.dump({'id' : response.json()['machineId']}, json_file)

    return render_template('pairing.html', pin=('%04d' % pin))

@interface_blueprint.route('/app/home')
def home():
    with open(os.path.dirname(__file__) + '/../../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)

        if not machine_info.get('plantingActive'):
            return render_template('planting.html')
    return render_template('home.html')

@interface_blueprint.route('/api/confirm_pairing')
def confirm_pairing():
    socketio.emit('device_paired', {'success': True})
    return jsonify({'success': True}), 200

@interface_blueprint.route('/app/wifi', methods=['GET', 'POST'])
def see_networks():
    cells = Cell.all('wlp3s0')

    if request.method == 'POST':
        form = request.form
        wanted_network = None

        for c in cells:
            if c.ssid == form['ssid']:
                wanted_network = c
                break

        if wanted_network is not None:
            scheme = Scheme.for_cell('wlp3s0', 'network', wanted_network, form['ssid'])
            scheme.save()
            scheme.activate()

            return render_template('wifi.html', success=True)

        return render_template('wifi.html', success=False)


    networks = []
    for c in cells:
        networks.append(c.ssid)

    return render_template('wifi.html', networks=networks)

@interface_blueprint.route('/app/key')
def keyboard():
    return render_template('keyboard.html')
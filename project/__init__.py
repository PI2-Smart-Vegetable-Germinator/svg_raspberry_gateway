import json
import os
import unittest
import subprocess

from flask import Flask
from flask import render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from datetime import datetime
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from dotenv import load_dotenv

load_dotenv()

socketio = SocketIO()

app_config = os.getenv('APP_SETTINGS')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config.from_object(app_config)

socketio.init_app(app)

CORS(app)

from project.api.images.views import image_blueprint
from project.interface.views import interface_blueprint
app.register_blueprint(image_blueprint)
app.register_blueprint(interface_blueprint)

from esp_commands.sensor_data import get_sensor_data
from esp_commands.sensor_data import check_illumination
from esp_commands.relays import start_irrigation

def get_updated_info():
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)
        if not machine_info.get('plantingId'):
            return
    sensor_info = get_sensor_data()
    data = {
        'currentTemperature': sensor_info.get('TemperaturaAr'),
        'currentHumidity': sensor_info.get('UmidadeSolo'),
        'currentAirHumidity': sensor_info.get('UmidadeAr'),
        'luxValue': sensor_info.get('Luximetro'),
    }

    # data = {
    #     'currentTemperature': 45,
    #     'currentHumidity': 10,
    #     'currentAirHumidity': 10,
    #     'luxValue': 5000,
    # }

    print(data)
    requests.post('http://localhost:5005/update_info', json=data, timeout=8)

def check_humidity(humidity):
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)
    
    if(machine_info.get('smartIrrigationEnabled')):
        if int(float(humidity)) < 70:
            latest_irrigation = machine_info.get('latestIrrigation')
            delta = datetime.now() - datetime.strptime(latest_irrigation, "%Y-%m-%d %H:%M:%S.%f")
            # checks if the latest irrigation has more than 5 minutes
            if(delta.seconds > 5*60):
                start_irrigation()
                # TODO send notification


@app.route('/update_info', methods=['POST'])
def update_info():
    post_data = request.get_json()
    data = {}
    check_humidity(post_data.get('currentHumidity'))
    illumination_time = check_illumination(post_data.get('luxValue'))
    post_data['illuminationTime'] = illumination_time
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)
        if not machine_info.get('plantingId'):
            return jsonify({'success': True, 'info': 'no planting active'}), 201
        post_data['plantingId'] = machine_info['plantingId']
        machine_info['lastUpdated'] = str(datetime.now())
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json', 'w') as json_file:
        json.dump(machine_info, json_file)
    socketio.emit('infoUpdated', post_data)

    data = {
        'currentTemperature': int(float(post_data.get('currentTemperature'))),
        'currentHumidity': int(float(post_data.get('currentHumidity'))),
        'currentAirHumidity': int(float(post_data.get('currentAirHumidity'))),
        'illuminationTime': post_data.get('illuminationTime'),
        'plantingId': post_data.get('plantingId')
    }
    
    requests.post('%s/api/update_planting_info' % os.getenv('EXTERNAL_GATEWAY_URL'), json=data, timeout=8)
    return jsonify({'success': True}), 201


cron = BackgroundScheduler()
cron.add_job(get_updated_info, 'interval', seconds=30)
cron.start()

if not os.path.exists('/etc/wpa_supplicant/wpa_supplicant.conf.backup'):
    subprocess.call(["sudo", "cp", "/etc/wpa_supplicant/wpa_supplicant.conf", "/etc/wpa_supplicant/wpa_supplicant.conf.backup"])


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/testsock')
def testsock():
    socketio.emit('test', {'test': 'test'})
    return jsonify({'test': 'test'}), 200


@app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('project/tests', pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

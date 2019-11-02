import json
import os
import unittest

from flask import Flask
from flask import render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

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

def get_updated_info():
    with open(os.path.dirname(__file__) + '/../test_data.json') as json_file:
        sensor_info = json.load(json_file)
        data = {
            'currentTemperature': sensor_info['temperature'],
            'currentHumidity': sensor_info['humidity'],
        }
        print(data)
    
    requests.post('http://localhost:5005/update_info', json=data)


@app.route('/update_info', methods=['POST'])
def update_info():
    post_data = request.get_json()
    with open(os.path.dirname(__file__) + '/../assets/machine_info.json') as json_file:
        machine_info = json.load(json_file)
        post_data['plantingId'] = machine_info['plantingId']
    socketio.emit('infoUpdated', request.get_json())
    requests.post('%s/api/update_planting_info' % os.getenv('EXTERNAL_GATEWAY_URL'), json=post_data)
    return jsonify({'success': True}), 201


cron = BackgroundScheduler()
cron.add_job(get_updated_info, 'interval', minutes=15)
cron.start()


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

import json
import os
import unittest

from flask import Flask
from flask import render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

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
    with open(os.path.dirname(__file__) + '../fake_data.json') as json_file:
        sensor_info = json.load(json_file)
        data = {
            'currentTemperature': sensor_info['temperature'],
            'currentHumidity': sensor_info['humidity'],
        }


cron = BackgroundScheduler()



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

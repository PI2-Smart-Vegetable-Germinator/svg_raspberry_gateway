from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from project import socketio

from random import randrange

interface_blueprint = Blueprint("interface", __name__)

@interface_blueprint.route('/app/start')
def start_system():
    return render_template('start_screen.html')

@interface_blueprint.route('/app/pairing')
def pair_device():
    pin = randrange(9999)
    return render_template('pairing.html', pin=('%04d' % pin))

@interface_blueprint.route('/app/home')
def home():
    return render_template('home.html')

@interface_blueprint.route('/api/confirm_pairing')
def confirm_pairing():
    socketio.emit('device_paired', {'success': True})
    return jsonify({'success': True}), 200
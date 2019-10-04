import os

from flask_cors import CORS

from flask import Blueprint
from flask import jsonify
from flask import request

import json

image_blueprint = Blueprint('image', __name__)
CORS(image_blueprint)

@image_blueprint.route('/api/submit_image', methods=['GET'])
def take_photo():
    
    return jsonify({
        'response': 'Image found!',
        'filename' : file.filename
    }), 200

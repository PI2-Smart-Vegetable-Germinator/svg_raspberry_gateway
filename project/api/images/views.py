import os

from flask_cors import CORS

from flask import Blueprint
from flask import jsonify
from flask import request

from project.api.images.image_capture import ImageCapture

import json

image_blueprint = Blueprint('image', __name__)
CORS(image_blueprint)

@image_blueprint.route('/api/take_photo', methods=['POST'])
def take_photo():
    image_capture = ImageCapture()
    
    # if(not image_capture.trigger_image_capture()):
    #     return jsonify({
    #         'response': 'Photo was not taken',
    #     }), 503
    post_data = request.get_json()
    print(post_data)
    response = image_capture.send_image(post_data['planting_id'])

    return jsonify(response.json()), response.status_code




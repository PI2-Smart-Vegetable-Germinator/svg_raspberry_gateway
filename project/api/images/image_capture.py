# from picamera.array import PiRGBArray
# from picamera import PiCamera
import requests
import time
import io
import os
import json

from flask import jsonify

class ImageCapture:
    def trigger_image_capture(self):
        # Open a file to replace the previous picture
        image_file = open('./project/api/images/assets/photo.jpg', 'wb')
        time.sleep(5)
        camera.capture(image_file)
        image_file.close()

        if os.path.exists('./project/api/images/assets/photo.jpg'):
            return True
        return False

    def send_image(self, planting_id):
        image_file = open('./project/api/images/assets/photo.jpg', 'rb')

        data = {
            'file': image_file,
            'json': (None,json.dumps({
                'planting_id': planting_id
            }), 'application/json')
        }

        response = requests.post('%s/api/submit_image' % os.getenv('EXTERNAL_GATEWAY_URL'), files = data)
        if(response.status_code != 200):
            return response
        
        image_file = open('./project/api/images/assets/photo.jpg', 'rb')

        data = {
            'file': image_file,
            'json': (None,json.dumps({
                'planting_id': planting_id
            }), 'application/json')
        }

        response = requests.post('%s/api/process_image_data' % os.getenv('EXTERNAL_GATEWAY_URL'), files = data)

        return response
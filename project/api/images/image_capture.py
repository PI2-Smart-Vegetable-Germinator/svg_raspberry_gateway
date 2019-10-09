# from picamera.array import PiRGBArray
# from picamera import PiCamera
import requests
import time
import io
import os

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
        response = requests.post('%s/api/submit_image' % os.getenv('EXTERNAL_GATEWAY_URL'), files = {'file': image_file}, json = {'planting_id' : planting_id})
        if (response.status_code != 200):
            return jsonify(response.json()), response.status_code
        #os.remove('./project/api/images/assets/photo.jpg')
        return jsonify({
            'response': 'Photo successfully sent',
        }), 200

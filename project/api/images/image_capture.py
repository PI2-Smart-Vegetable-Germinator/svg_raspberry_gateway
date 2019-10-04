# from picamera.array import PiRGBArray
# from picamera import PiCamera
import requests
import time
import io
import os

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

    def send_image(self):
        image_file = open('./project/api/images/assets/photo.jpg', 'rb')
        response = requests.post(url = 'http://localhost:5000/api/send_image', files = image_file)
        if (response.status_code != 200):
            return response
        os.remove('./project/api/images/assets/photo.jpg')
        return jsonify({
            'response': 'Photo successfully sent',
        }), 200

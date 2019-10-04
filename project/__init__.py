import os
import unittest

from flask import Flask
from flask_cors import CORS

app_config = os.getenv('APP_SETTINGS')
app = Flask(__name__)
app.config.from_object(app_config)

CORS(app)

from project.api.images.views import image_blueprint
app.register_blueprint(image_blueprint)

@app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('project/tests', pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

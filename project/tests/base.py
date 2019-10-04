from flask import Flask

from flask_jwt_extended import JWTManager

from flask_testing import TestCase

from project import db


class BaseTestCase(TestCase):
    def create_app(self):
        app = Flask(__name__)

        jwt = JWTManager()

        app.config.from_object('project.config.TestConfig')

        db.init_app(app)
        jwt.init_app(app)

        from project.api.auth.views import auth_blueprint
        app.register_blueprint(auth_blueprint)

        return app
    
    def setUp(self):
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()


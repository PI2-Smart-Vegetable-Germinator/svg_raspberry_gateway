from flask.cli import FlaskGroup
from project import app
from project import socketio


if __name__ == "__main__":
    socketio.run(app, debug=True)

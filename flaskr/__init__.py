from flask import Flask

import os
import configparser

config = configparser.ConfigParser()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get the StudyShare directory
config.read(os.path.join(base_dir, ".ini"))  # Read the .ini file

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']
    app.config['DB_NAME'] = config['PROD']['DB_NAME']

    from . import db
    db.init_app(app)

    return app
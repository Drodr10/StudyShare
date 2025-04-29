from flask import Flask
from dotenv import load_dotenv
import os
import configparser

load_dotenv()  # Load environment variables from .env file

config = configparser.ConfigParser()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get the StudyShare directory
config.read(os.path.join(base_dir, ".ini"))  # Read the .ini file

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']
    app.config['DB_NAME'] = config['PROD']['DB_NAME']
    
    # Set the secret keys from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    
    from . import post
    app.register_blueprint(post.bp)
    app.add_url_rule('/', endpoint='post.index')

    return app
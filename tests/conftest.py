import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flaskr import create_app
from flaskr.db import get_db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_studyshare'
    app.config['DB_NAME'] = 'test_studyshare'
    app.config['SECRET_KEY'] = 'abcdef12345678901'
    app.config['JWT_SECRET_KEY'] = 'abcdef12345678902'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clear_db(app):
    with app.app_context():
        db = get_db()
        db.client.drop_database('test_studyshare')  # Clear the test database before each test
        from flaskr.db import init_db
        init_db()
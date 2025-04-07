from flaskr.db import get_db, close_db, init_db
from flask import g

def test_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is not None
        close_db()
        assert 'db' not in g
        
def test_init_db_command(app):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['init-db', '--test'])
        assert 'Initialized the database.' in result.output
    
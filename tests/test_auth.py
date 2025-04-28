import datetime
import jwt
from mongomock import DuplicateKeyError

from flaskr.auth import login_required


def test_login(client):
    """
    Test the login functionality.
    """
    # Register a user first
    client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })

    # Test successful login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect to dashboard
    assert response.headers['Location'] == '/dashboard'

    # Test invalid login (wrong password)
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Stay on the login page
    assert b"Incorrect password." in response.data

    # Test invalid login (nonexistent username)
    response = client.post('/auth/login', data={
        'username': 'nonexistentuser',
        'password': 'password123'
    })
    assert response.status_code == 200  # Stay on the login page
    assert b"Incorrect username." in response.data

    # Test missing fields
    response = client.post('/auth/login', data={
        'username': ''
    })
    assert response.status_code == 200  # Stay on the login page
    assert b"Enter username and password." in response.data

    # Test already logged-in user
    with client.session_transaction() as session:
        session['username'] = 'testuser'
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect to dashboard
    assert response.headers['Location'] == '/dashboard'
    
def test_register(client):
    """
    Test the registration functionality.
    """
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/login'  # Redirect to the login page

    # Test duplicate username
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'newemail@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200  # Stay on the registration page
    assert b"Username or email already exists." in response.data  # Check for error message
    
    # Test invalid username
    response = client.post('/auth/register', data={
        'username': 'invalid$username',
        'email': 'testemail@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200  # Stay on the registration page
    assert b"Username can only contain characters, numbers, and underscores." in response.data
        
    # Test invalid email format
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'invalidemail',
        'password': 'password123'
    })
    assert response.status_code == 200  # Stay on the registration page
    assert b"Invalid email!" in response.data
    
    # Test short password
    response = client.post('/auth/register', data={
        'username': 'shortpassuser',
        'email': 'short@email.com',
        'password': 'short'
    })
    assert response.status_code == 200  # Stay on the registration page
    assert b"Password must be longer than 7 characters." in response.data
    
    # Test missing fields
    response = client.post('/auth/register', data={
        'username': '',
        'email': '',
        'password': ''
    })
    assert response.status_code == 200  # Stay on the registration page
    assert b"Enter username, email, and password." in response.data
    
    # Test standard exception handling
    from unittest.mock import patch
    with patch('flaskr.auth.get_db') as mock_get_db:
        mock_get_db.return_value.users.insert_one.side_effect = Exception("Database error")
        
        response = client.post('/auth/register', data={
            'username': 'erroruser',
            'email': 'error@example.com',
            'password': 'error123'
        })
        assert response.status_code == 200  # Stay on the registration page
        assert b"An unknown error occurred." in response.data
    
    # Unknown Duplicate error handling
    with patch('flaskr.auth.get_db') as mock_get_db:
        mock_get_db.return_value.users.insert_one.side_effect = DuplicateKeyError("Duplicate key error")
        
        response = client.post('/auth/register', data={
            'username': 'duplicateusernow',
            'email': 'goodemail@email.com',
            'password': 'goodpassword123'
        })
        assert response.status_code == 200  # Stay on the registration page
        assert b"An unknown error occurred." in response.data
    
def test_logout(client):
    """
    Test the logout functionality.
    """
    # Simulate a logged-in user
    with client.session_transaction() as session:
        session['user_id'] = 'some_user_id'
        session['username'] = 'testuser'
        session['logged_in'] = True

    # Test logout
    response = client.get('/auth/logout')
    assert response.status_code == 302  # Redirect to login page
    assert response.headers['Location'] == '/auth/login'

    # Ensure session is cleared
    with client.session_transaction() as session:
        assert 'user_id' not in session
        assert 'username' not in session
        assert 'logged_in' not in session
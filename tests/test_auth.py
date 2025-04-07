def test_login(client):
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
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/dashboard'  # Redirect to the dashboard

    # Test invalid login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/login'  # Redirect back to the login page
    
    # Test missing fields
    response = client.post('/auth/login', data={
        'username': 'testuser'
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/login'  # Redirect back to the login page
    
def test_register(client):
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
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/register'  # Redirect back to the registration page
    
    # Test invalid email format
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'invalidemail',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/register'  # Redirect back to the registration page
    
    # Test standard exception handling
    from unittest.mock import patch
    with patch('flaskr.auth.get_db') as mock_get_db:
        mock_get_db.return_value.users.insert_one.side_effect = Exception("Database error")
        
        response = client.post('/auth/register', data={
            'username': 'erroruser',
            'email': 'error@example.com',
            'password': 'error123'
        })
        assert response.status_code == 302  # Redirect
        assert response.headers['Location'] == '/auth/register'
    
    
def test_logout(client):
    # Simulate a logged-in user
    with client.session_transaction() as session:
        session['user_id'] = 'some_user_id'

    response = client.post('/auth/logout')
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == '/auth/login'  # Redirect to the login page
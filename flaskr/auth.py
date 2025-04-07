import functools
import re
import datetime
import jwt

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session
from .db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError


bp = Blueprint('auth', __name__, url_prefix='/auth')

def redirect_to_login():
    return redirect(url_for('auth.login'))

def redirect_to_registration():
    return redirect(url_for('auth.register'))

@bp.route('/login', methods=('POST',))
def login():
    """
    Login a user with username and password.
    """
    db = get_db()
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return redirect_to_login()  # Redirect back to the login page
    
    # Make sure the user exists
    user = db.users.find_one({"username": username})
    
    if user and check_password_hash(user['password'], password):
        # Generate a JWT token
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Store the token in the session
        session['jwt_token'] = token
        return redirect(url_for('dashboard.index'))
    else:
        return redirect_to_login() 

    
@bp.route('/register', methods=('POST',))
def register():
    """
    Register a new user with username, email, and password.
    """
    db = get_db()
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not all([username, email, password]) or \
       not re.match(r"^\w+$", username) or \
       not re.match(r"[^@]+@[^@]+\.[^@]+", email) or \
       len(password) < 8:
        return redirect_to_registration()
    
    # Hash the password and store the user in the database
    hashed_password = generate_password_hash(password)
    
    try:
        db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
    except DuplicateKeyError as e:
        if "username" in str(e) or "email" in str(e):
            return redirect_to_registration()
    except Exception as e:
        return redirect_to_registration()
    
    return redirect_to_login() 

@bp.route('/logout', methods=('POST',))
def logout():
    """
    Logout a user.
    """
    
    session.clear()
    return redirect_to_login()
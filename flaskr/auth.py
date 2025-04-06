import functools
import re
import jwt
import datetime

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session
from .db import get_db
from werkzeug.security import generate_password_hash, check_password_hash



bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('POST',))
def login():
    """
    Login a user with username and password.
    """
    db = get_db()
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({"message": "Please provide username and password"}), 400
    
    # Make sure the user exists
    user = db.users.find_one({"username": username})
    
    if user and check_password_hash(user['password'], password):
        # Generate a JWT token
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401
    
@bp.route('/register', methods=('POST',))
def register():
    """
    Register a new user with username, email, and password.
    """
    db = get_db()
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not username or not email or not password:
        return jsonify({"message": "Please provide username, email, and password"}), 400
    
    if not re.match(r"^\w+$", username):
        return jsonify({"message": "Username can only contain letters, numbers, and underscores"}), 400
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email address"}), 400
    
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long"}), 400
    
    # Check if the user already exists
    if db.users.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 409
    
    if db.users.find_one({"email": email}):
        return jsonify({"message": "Email already exists"}), 409
    
    # Hash the password and store the user in the database
    hashed_password = generate_password_hash(password)
    
    try:
        db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
    except Exception as e:
        return jsonify({"message": "Error registering user", "error": str(e)}), 500

    # Verification email? Maybe later
    
    return jsonify({"message": "User registered successfully"}), 201

@bp.route('/logout', methods=('POST',))
def logout():
    """
    Logout a user.
    """
    # Invalidate the JWT token (this can be done by adding it to a blacklist)
    return jsonify({"message": "Logout successful"}), 200
import functools
import re
import datetime
import jwt

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session, flash
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
        flash("Please enter an username or password")
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
        flash("Incorrect username or password.")
        return redirect_to_login() 

    
@bp.route('/register', methods=('POST',))
def register():
    """
    Register a new user with username, email, and password.
    """
    db = get_db()
    error = None
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not all([username, email, password]): 
        error = "Enter username, email, and password."
    elif re.match(r"[a-zA-Z0-9_]+$", username) :
        error = "Username can only contain characters, numbers, and underscores."
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email) :
        error = "Invalid email!"
    elif len(password) < 8:
        error = "Password must be longer than 7 characters."
    
    # Hash the password and store the user in the database
    hashed_password = generate_password_hash(password)
    if error is None:
        try:
            db.users.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password
            })
        except DuplicateKeyError as e:
            if "username" in str(e) or "email" in str(e):
                flash("Username or email already exists.")
                return redirect_to_registration()
        except Exception as e:
            return redirect_to_registration()
        return redirect_to_login()
    flash(error)
    return redirect_to_registration() 

@bp.route('/logout', methods=('POST',))
def logout():
    """
    Logout a user.
    """
    
    session.clear()
    return redirect_to_login()

def login_required(view):
    """
    Decorator to ensure the user is logged in.
    If not, redirect to the login page.
    """
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        token = session.get('jwt_token')
        if not token:
            return redirect_to_login()       
        try:
            jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            flash("Session expired. Please log in again.")
            return redirect_to_login()
        except jwt.InvalidTokenError:
            flash("Invalid token. Please log in again.")
            return redirect_to_login()
        return view(*args, **kwargs)
    return wrapped_view


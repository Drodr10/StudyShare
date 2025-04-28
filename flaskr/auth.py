import functools
import re
import datetime
import jwt

from flask import Blueprint, g, request, render_template, current_app, redirect, url_for, session, flash
from .db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from markupsafe import escape


bp = Blueprint('auth', __name__, url_prefix='/auth')

def redirect_to_login():
    return redirect(url_for('auth.login'))

def redirect_to_registration():
    return redirect(url_for('auth.register'))

@bp.route('/login', methods=('GET','POST'))
def login():
    """
    Login a user with username and password.
    """
    if request.method == 'POST':
        db = get_db()
        
        username = escape(request.form.get('username'))
        password = escape(request.form.get('password'))
        
        error = None
        
        if not username or not password:
            error = "Enter username and password."
        
        else:
            # Make sure the user exists
            user = db.users.find_one({"username": username})
            
            if user is None:
                error = "Incorrect username."
                
            elif not check_password_hash(user['password'], password):
                error = "Incorrect password."
            
        
        if error is None:
            # Check if the user is already logged in
            if session.get('username') == username:
                flash("You are already logged in.")
                return redirect(url_for('dashboard.index'))
            
            # Generate a JWT token
            token = jwt.encode({
                "username": username,
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
            
            # Store the token in the session
            session.clear()
            session['jwt_token'] = token
            session['username'] = username
            session['user_id'] = str(user['_id'])
            session['logged_in'] = True
            return redirect(url_for('dashboard.index'))
        
        flash(error) 
        
    return render_template('auth/login.html')

    
@bp.route('/register', methods=('GET','POST'))
def register():
    """
    Register a new user with username, email, and password.
    """
    if request.method == 'POST':
        db = get_db()
        error = None
        
        username = escape(request.form.get('username'))
        email = escape(request.form.get('email'))
        password = escape(request.form.get('password'))
        
        if not all([username, email, password]): 
            error = "Enter username, email, and password."
        elif not re.match(r"^\w+$", username) :
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
                    error = "Username or email already exists."
                else:
                    error = "An unknown error occurred."
            except Exception as e:
                error = "An unknown error occurred."
            else:
                return redirect_to_login()
        flash(error)
        
    return render_template('auth/register.html')

@bp.before_app_request
def load_logged_in_user():
    """
    Load the logged-in user from the session.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        if 'user_data' in session:
            g.user = session['user_data']
        else:
            db = get_db()
            g.user = db.users.find_one({"_id": user_id})
            if g.user:
                session['user_data'] = {
                    'username': g.user['username'],
                    'email': g.user['email'],
                    'user_id': str(g.user['_id'])
                }
            else:
                g.user = None

@bp.route('/logout')
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
        if g.user is None:
            flash("You need to be logged in to access this page.")
            return redirect_to_login()
        
        # Check if the JWT token is valid
        token = session.get('jwt_token')
        if token:
            try:
                jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                flash("Your session has expired. Please log in again.")
                return redirect_to_login()
            except jwt.InvalidTokenError:
                flash("Invalid token. Please log in again.")
                return redirect_to_login()
        
        # If the token is valid, proceed to the view
        return view(*args, **kwargs)
    return wrapped_view
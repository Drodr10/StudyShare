from flask import Blueprint

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('', methods=('GET',))
def index():
    """
    Dashboard page for logged-in users.
    """
    return "Welcome to your dashboard!"
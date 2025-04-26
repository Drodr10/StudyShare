from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('', methods=('GET',))
def index():
    """
    Dashboard page for logged-in users.
    """
    return render_template('base.html')


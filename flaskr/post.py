from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('post', __name__, url_prefix='/post')

@bp.route('/')
def index():
    """
    Display all posts.
    Order posts by creation date in descending order.
    """
    db = get_db()
    posts = db.posts.find().sort('created_at', -1)
    
    posts = [serialize_post(post) for post in posts]
    
    return render_template('post/index.html', posts=posts)

def serialize_post(post):
    return {
        'id': str(post['_id']),
        'title': post['title'],
        'content': post['content'],
        'category': post['category'],
        'creator_id': str(post['creator_id']),
        'created_at': post['created_at'],
        'updated_at': post['updated_at'],
        'tags': post.get('tags', []),
    }
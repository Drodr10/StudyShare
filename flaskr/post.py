from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.exceptions import abort
from datetime import datetime

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

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            now = datetime.now(datetime.timezone.utc)
            db = get_db()
            db.posts.insert_one({
                'title': title,
                'content': body,
                'category': request.form.get('category', 'Uncategorized'),
                'creator_id': g.user['_id'],  
                'created_at': now,
                'updated_at': now,
                'tags': request.form.getlist('tags') 
            })
            return redirect(url_for('post.index'))

    return render_template('post/create.html')

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
    

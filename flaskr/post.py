from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.exceptions import abort
from datetime import datetime, timezone
from bson.objectid import ObjectId

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
            now = datetime.now(timezone.utc)
            db = get_db()
            db.posts.insert_one({
                'title': title,
                'content': body,
                'category': request.form.get('category', 'Uncategorized'),
                'creator_id': g.user['user_id'],  
                'created_at': now,
                'updated_at': now,
                'tags': request.form.getlist('tags') 
            })
            flash('Post created successfully.')
            return redirect(url_for('post.index'))

    return render_template('post/create.html')

@bp.route('/<post_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(post_id):
    db = get_db()
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    categories = list(db.categories.find())

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")
    if post['creator_id'] != g.user['user_id']:
        abort(403, "You do not have permission to edit this post.")
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        tags = request.form['tags'].split(',')
        
        db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': title,
                'content': content,
                'category': category,
                'tags': [tag.strip() for tag in tags],
                'updated_at': datetime.now(timezone.utc)
            }}
        )
        flash('Post updated successfully.')
        return redirect(url_for('post.index'))
    return render_template('post/edit.html', post=serialize_post(post), categories=categories)

@bp.route('/<post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()

    db.posts.delete_one({'_id': ObjectId(post_id)})
    
    flash('Post deleted successfully.')
    return redirect(url_for('post.index'))

        


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

def get_post(post_id, check_auth=True):
    """
    Retrieve a post by its ID.
    Optionally check if the current user is authorized to access the post.
    """
    db = get_db()
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    
    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")
    
    if check_auth and post['creator_id'] != g.user['user_id']:
        abort(403, "You do not have permission to access this post.")
    
    return serialize_post(post)


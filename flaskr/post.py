from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.exceptions import abort
from datetime import datetime, timezone
from bson.objectid import ObjectId
import re
import markdown

from flaskr.db import get_db
from flaskr.auth import login_required



bp = Blueprint('post', __name__, url_prefix='/post')

@bp.route('/')
def index():
    """
    Display all posts.
    Allows searching by title, content, tags, and category.
    Supports sorting by relevance, popularity, title, or created_at.
    """
    search_query = request.args.get('q', '').strip()
    require_all_tags = request.args.get('require_all_tags', 'false') == 'true'
    search_tags = request.args.getlist('tags')
    search_category = request.args.get('category', '')
    search_sort = request.args.get('sort', 'created_at')
    
    mongo_query = {}
    
    if search_query:
        escaped_query = re.escape(search_query)
        mongo_query['$or'] = [
            {'title': {'$regex': escaped_query, '$options': 'i'}},
            {'content': {'$regex': escaped_query, '$options': 'i'}}
        ]
    
    if search_tags:
        cleaned_tags = [tag.strip() for tag in search_tags if tag.strip()]
        if cleaned_tags:
            if require_all_tags:
                mongo_query['tags'] = {'$all': cleaned_tags}
            else:
                mongo_query['tags'] = {'$in': cleaned_tags}
    
    if search_category:
        mongo_query['category'] = search_category
    
    db = get_db()
    posts = None
    
    final_query = mongo_query.copy()
    
    if search_sort == 'relevance':
        if search_query:
            text_search_query = final_query.copy()
            # $or condition CANNOT be used with $text search in MongoDB
            text_search_query.pop('$or', None)  # Remove the $or key if it exists
            
            text_search_query['$text'] = {'$search': search_query}
            
            try:    
                posts = db.posts.find(
                    text_search_query, 
                    {'score': {'$meta': 'textScore'}}
                ).sort([('score', {'$meta': 'textScore'})])
            except Exception as e:
                flash(f"An error occurred while fetching posts sorted by relevance: {str(e)}")
                try:
                    posts = db.posts.find(mongo_query).sort('created_at', -1)
                except Exception as e_fallback:
                    flash(f"An error occurred while fetching posts: {str(e_fallback)}")
                    posts = []
        else:
            flash("Search query is empty. Defaulting to time sort.")
            try:
                posts = db.posts.find(mongo_query).sort('created_at', -1)
            except Exception as e:
                flash(f"An error occurred while fetching posts: {str(e)}")
                posts = []
        
    elif search_sort == 'popularity':
        try:
            posts = db.posts.aggregate([
                {'$match': mongo_query or {}},
                {'$lookup': {
                    'from': 'likes',
                    'localField': '_id',
                    'foreignField': 'post_id',
                    'as': 'likes'
                }},
                {'$addFields': {'like_count': {'$size': '$likes'}}},
                {'$sort': {'like_count': -1}}
            ])
        except Exception as e:
            flash(f"An error occurred while fetching posts sorted by popularity: {str(e)}")
            try:
                posts = db.posts.find(mongo_query).sort('created_at', -1)
            except Exception as e_fallback:
                flash(f"An error occurred while fetching posts: {str(e_fallback)}")
                posts = []
    
    elif search_sort in ['title', 'created_at']:
        try:
            posts = db.posts.find(mongo_query).sort(search_sort, -1)
        except Exception as e:
            flash(f"An error occurred while fetching posts sorted by {search_sort}: {str(e)}")
            posts = []
    else:
        flash("Invalid sort option. Defaulting to time sort.")
        try:
            posts = db.posts.find(mongo_query).sort('created_at', -1)
        except Exception as e:
            flash(f"An error occurred while fetching posts: {str(e)}")
            posts = []
    
    search_query = request.args.get('q', '')
    search_tags = request.args.getlist('tags')
    
    posts = [serialize_post(post) for post in posts]
    
    return render_template('post/index.html',
                           posts=posts,
                           search_query=search_query,
                           require_all_tags=require_all_tags,
                           search_tags=search_tags,
                           search_category=search_category,
                           categories=list(db.categories.find()))

@bp.route('/<post_id>/view', methods=('GET',))
@login_required
def view(post_id):
    """
    View a specific post by its ID, but only if it was not created by the current user.
    """
    db = get_db()
    post = db.posts.find_one({'_id': ObjectId(post_id)})

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")
        
    return render_template('post/view.html', post=serialize_post(post))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        content  = request.form['content']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            now = datetime.now(timezone.utc)
            now = now.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
            db.posts.insert_one({
                'title': title,
                'content': content,
                'category': request.form.get('category', 'Uncategorized'),
                'creator_id': g.user['user_id'],  
                'created_at': now,
                'updated_at': now,
                'tags': request.form.getlist('tags'),
                'likes': 0,
                'comments': 0 
            })
            flash('Post created successfully.')
            return redirect(url_for('post.index'))

    return render_template('post/create.html', categories=list(db.categories.find()))

@bp.route('/<post_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(post_id):
    db = get_db()
    post = get_post(post_id)
    
    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")
    if post['creator_id'] != g.user['user_id']:
        abort(403, "You do not have permission to edit this post.")
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        tags = request.form['tags'].split(',')
        
        now = datetime.now(timezone.utc)
        now = now.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
        db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': title,
                'content': content,
                'category': category,
                'tags': [tag.strip() for tag in tags],
                'updated_at': now
            }}
        )
        flash('Post updated successfully.')
        return redirect(url_for('post.index'))
    return render_template('post/edit.html', post=serialize_post(post), categories=list(db.categories.find()))

@bp.route('/<post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()

    db.posts.delete_one({'_id': ObjectId(post_id)})
    
    flash('Post deleted successfully.')
    return redirect(url_for('post.index'))

@bp.route('/<post_id>/like', methods=('POST',))
@login_required
def like_post(post_id):
    db = get_db()
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    
    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")
    
    like = db.likes.find_one({'post_id': ObjectId(post_id), 'user_id': g.user['user_id']})
    
    if like:
        # User already liked the post, so remove the like
        db.likes.delete_one({'post_id': ObjectId(post_id), 'user_id': g.user['user_id']})
        db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'likes': -1}})
        flash('Post unliked successfully.')
    else:
        # User has not liked the post yet, so add the like
        db.likes.insert_one({'post_id': ObjectId(post_id), 'user_id': g.user['user_id']})
        db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'likes': 1}})
        flash('Post liked successfully.')
    
    return redirect(url_for('post.view', post_id = post_id))

        


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
        'comments': post.get('comments', []),
        'likes': post.get('likes', [])
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


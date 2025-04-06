import click

from flask import current_app, g
from pymongo import MongoClient

def get_db():
    """
    Configuration method to return db instance
    """
    if 'db' not in g:
        # Create a new database connection if it doesn't exist yet
        client = MongoClient(current_app.config['MONGO_URI'])
        db_name = current_app.config['DB_NAME']
        
        g.db = client[db_name]
        # Store the client in the Flask global context for later use
        g.client = client
    
    return g.db

def close_db(e=None):
    """
    Close the database connection
    """
    client = g.pop('client', None)

    if client is not None:
        client.close()
        
def init_db():
    """
    Initialize the database with the schema and data
    """
    db = get_db()

    if 'users' not in db.list_collection_names():
        # Create the 'users' collection
        db.create_collection('users')
        print("Created 'users' collection.")

    # MongoDB will skip creating the index if it already exists
    db.users.create_index([('username', 1)], unique=True)
    db.users.create_index([('email', 1)], unique=True)
    db.users.create_index([('password', 1)])
    
    
    if 'posts' not in db.list_collection_names():
        # Create the 'posts' collection
        db.create_collection('posts')
        print("Created 'posts' collection.")
    
    db.posts.create_index([('title', 1)])
    db.posts.create_index([('category', 1)])
    db.posts.create_index([('content', 1)])
    db.posts.create_index([('creator_id', 1)])
    db.posts.create_index([('created_at', 1)])
    db.posts.create_index([('updated_at', 1)])
    db.posts.create_index([('tags', 1)])
    
    if 'comments' not in db.list_collection_names():
        db.create_collection('comments')
        print("Created 'comments' collection.")
    
    db.comments.create_index([('post_id', 1)])
    db.comments.create_index([('creator_id', 1)])

    if 'likes' not in db.list_collection_names():
        db.create_collection('likes')
        print("Created 'likes' collection.")
    
    db.likes.create_index([('post_id', 1)])
    db.likes.create_index([('user_id', 1)])
    db.likes.create_index([('post_id', 1), ('user_id', 1)], unique=True)  # Ensure a user can like a post only once

    if 'categories' not in db.list_collection_names():
        db.create_collection('categories')
        print("Created 'categories' collection.")
    
    db.categories.create_index([('name', 1)], unique=True)
    
@click.command('init-db')
def init_db_command():
    """
    Command line interface to initialize the database
    """
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    """
    Initialize the Flask application with the database
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
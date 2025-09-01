# File: config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Get the database URL from the environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Render's free PostgreSQL provides a URL starting with 'postgres://'
    # SQLAlchemy 2.0 prefers 'postgresql://', so we'll replace it if it exists.
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Use the production database URL if available, otherwise fall back to local SQLite
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
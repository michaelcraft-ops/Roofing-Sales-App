# File: app/__init__.py

# This file initializes our Flask application and brings together the different components.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_login import LoginManager

# Create the main Flask application instance
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# --- Configuration ---
app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../instance/site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database & Migration Engine Initialization ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# --- THIS IS THE FIX ---
# Tell Flask-Login which page to redirect to for login.
login.login_view = 'login'
# --- END OF FIX ---

# We import the routes and models here at the bottom to avoid circular import errors.
from app import routes, models










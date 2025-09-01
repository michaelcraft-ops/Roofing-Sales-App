# File: app/__init__.py

# This file initializes our Flask application and brings together the different components.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config  # <-- IMPORT THE NEW CONFIG

# Create the main Flask application instance
app = Flask(__name__)
app.config.from_object(Config) # <-- APPLY CONFIG FROM THE FILE

# --- Database & Migration Engine Initialization ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# Tell Flask-Login which page to redirect to for login.
login.login_view = 'login'

# We import the routes and models here at the bottom to avoid circular import errors.
from app import routes, models










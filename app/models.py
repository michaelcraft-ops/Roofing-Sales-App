# File: app/models.py

from datetime import datetime
from app import db
import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login # We will create this in the next step

# NEW: Flask-Login requires a 'user_loader' function to get a user by their ID.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# NEW: The User Model
# We are inheriting from UserMixin to get standard user session management methods
# required by Flask-Login.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    # Define the one-to-many relationships. One user can have many leads, activities, etc.
    leads = db.relationship('Lead', backref='author', lazy='dynamic')
    daily_activities = db.relationship('DailyActivity', backref='author', lazy='dynamic')
    settings = db.relationship('Settings', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deals = db.relationship('Deal', backref='lead', lazy=True, cascade="all, delete-orphan")
    
    # NEW: Foreign key to link leads to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Lead {self.first_name} {self.last_name}>'

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default='Lead')
    contract_price = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate = db.Column(db.Float, nullable=False, default=0.10)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)

    def __repr__(self):
        return f'<Deal {self.id} for Lead {self.lead_id}>'

class DailyActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=dt.date.today)
    doors_knocked = db.Column(db.Integer, default=0)
    appointments_set = db.Column(db.Integer, default=0)

    # NEW: Foreign key to link daily activity to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<DailyActivity {self.date}>'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annual_income_goal = db.Column(db.Float, default=100000.0)

    # NEW: Foreign key to link settings to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

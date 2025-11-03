# File: app/models.py

from datetime import datetime
import datetime as dt

from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# ---- Shared status vocabulary (used by Lead and Deal) ----
LEAD_STATUSES = ["New", "Contacted", "Appt", "Signed", "Completed"]
LEAD_STATUS_ORDER = {s: i for i, s in enumerate(LEAD_STATUSES)}


# Flask-Login loader
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# -----------------------------
# User
# -----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    # relationships
    leads = db.relationship('Lead', backref='author', lazy='dynamic')
    daily_activities = db.relationship('DailyActivity', backref='author', lazy='dynamic')
    settings = db.relationship('Settings', backref='author', lazy='dynamic')

    # defaults for projector/commission logic
    company_margin = db.Column(db.Float, nullable=False, default=30.0)   # percent
    commission_rate = db.Column(db.Float, nullable=False, default=40.0)  # percent

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# -----------------------------
# Lead
# -----------------------------
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # status at lead level (shared vocabulary)
    status = db.Column(db.String(20), nullable=False, default='New')

    # relationships
    deals = db.relationship('Deal', backref='lead', lazy=True, cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self):
        return f'<Lead {self.first_name} {self.last_name}>'


# -----------------------------
# Deal
# -----------------------------
class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Use the same vocabulary as leads. Keep String(50) to avoid DB migrations for length.
    status = db.Column(db.String(50), nullable=False, default='New')

    contract_price = db.Column(db.Float, nullable=False, default=0.0)
    commission_rate = db.Column(db.Float, nullable=False, default=0.10)  # percent
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)

    # projector parity
    commission_base = db.Column(db.String(20), nullable=False, default='profit')  # 'profit' | 'revenue'
    company_margin = db.Column(db.Float, nullable=False, default=30.0)            # percent

    def __repr__(self):
        return f'<Deal {self.id} for Lead {self.lead_id}>'


# -----------------------------
# Daily Activity
# -----------------------------
class DailyActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=dt.date.today)
    doors_knocked = db.Column(db.Integer, default=0)
    appointments_set = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<DailyActivity {self.date}>'


# -----------------------------
# Settings
# -----------------------------
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annual_income_goal = db.Column(db.Float, default=100000.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

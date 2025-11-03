# File: app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, IntegerField,
    TextAreaField, DecimalField, SelectField, FloatField, RadioField
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Optional
from app.models import User, LEAD_STATUSES  # shared status list

# Shared status choices for Lead and Deal
STATUS_CHOICES = [(s, s) for s in LEAD_STATUSES]

# -----------------------------
# Leads
# -----------------------------
class LeadForm(FlaskForm):
    first_name   = StringField('First Name', validators=[DataRequired()])
    last_name    = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    email        = StringField('Email', validators=[Optional(), Email()])
    address      = StringField('Address', validators=[Optional()])
    notes        = TextAreaField('Notes', validators=[Optional()])
    status       = SelectField('Status', choices=STATUS_CHOICES, default='New', validators=[DataRequired()])
    submit       = SubmitField('Save')

# LeadStatusForm removed. Use LeadForm for create and edit.

# -----------------------------
# Deals
# -----------------------------
class DealForm(FlaskForm):
    status = SelectField('Status', choices=STATUS_CHOICES, validators=[DataRequired()])
    contract_price = FloatField('Contract Price ($)', validators=[Optional()])
    commission_base = RadioField(
        'Commission Base',
        choices=[('profit', 'Company profit'), ('revenue', 'Total sales price / RCV')],
        default='profit',
        validators=[DataRequired()],
    )
    company_margin = FloatField('Company Margin (%)', default=30.0, validators=[NumberRange(min=0, max=100)])
    commission_rate = FloatField('Commission Rate (%)', default=40.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Changes')

    def validate(self, **kwargs):
        rv = super().validate(**kwargs)
        if not rv:
            return False
        if (self.status.data == 'Completed' and
                (self.contract_price.data is None or self.contract_price.data <= 0)):
            self.contract_price.errors.append('Contract price is required for completed jobs.')
            return False
        return True

# -----------------------------
# Settings / Activity
# -----------------------------
class SettingsForm(FlaskForm):
    annual_income_goal = FloatField('Annual Income Goal ($)', validators=[DataRequired()])
    submit = SubmitField('Update Goal')

class DailyActivityForm(FlaskForm):
    doors_knocked = IntegerField("Doors Knocked Today", validators=[DataRequired()])
    appointments_set = IntegerField("Appointments Set Today", validators=[DataRequired()])
    submit = SubmitField('Log Activity')

# -----------------------------
# Auth
# -----------------------------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Please use a different email address.')

# -----------------------------
# Manual projector
# -----------------------------
class ManualProjectorForm(FlaskForm):
    income_goal = DecimalField('Annual Income Goal ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    days_to_forecast = IntegerField('Number of Days to Forecast', validators=[DataRequired(), NumberRange(min=1)])

    commission_base = RadioField('Commission Base',
        choices=[('profit', 'Company profit'), ('revenue', 'Total sales price / RCV')],
        default='profit', validators=[DataRequired()])
    company_margin = DecimalField('Company margin (%)', validators=[NumberRange(min=0, max=100)], default=30, places=1)
    commission_rate = DecimalField('Commission rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=40, places=1)

    doors_knocked    = IntegerField('Historical: Total Doors Knocked',    validators=[DataRequired(), NumberRange(min=1)])
    appointments_set = IntegerField('Historical: Total Appointments Set', validators=[DataRequired(), NumberRange(min=1)])
    deals_signed     = IntegerField('Historical: Total Deals Signed',     validators=[DataRequired(), NumberRange(min=1)])
    deals_completed  = IntegerField('Historical: Total Deals Completed',  validators=[DataRequired(), NumberRange(min=1)])
    total_rcv        = DecimalField('Historical: Total RCV from Completed Deals ($)', validators=[DataRequired(), NumberRange(min=1)], places=2)

    submit = SubmitField('Calculate Forecast')


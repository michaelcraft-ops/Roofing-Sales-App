# File: app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, DecimalField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from app.models import User # NEW: Import the User model to check for existing users


# --- Lead Form ---
class LeadForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Address', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Submit')

# --- Deal Form ---
class DealForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Lead', 'Lead'),
        ('Appointment Set', 'Appointment Set'),
        ('Contract Signed', 'Contract Signed'),
        ('Job Completed', 'Job Completed'),
        ('Deal Lost', 'Deal Lost')
    ], validators=[DataRequired()])
    contract_price = FloatField('Contract Price ($)', validators=[DataRequired()])
    commission_rate = FloatField('Commission Rate (%)', default=10.0, validators=[DataRequired()])
    submit = SubmitField('Create Deal')

# --- Settings Form ---
class SettingsForm(FlaskForm):
    annual_income_goal = FloatField('Annual Income Goal ($)', validators=[DataRequired()])
    submit = SubmitField('Update Goal')

# --- Daily Activity Form ---
class DailyActivityForm(FlaskForm):
    doors_knocked = IntegerField("Doors Knocked Today", validators=[DataRequired()])
    appointments_set = IntegerField("Appointments Set Today", validators=[DataRequired()])
    submit = SubmitField('Log Activity')


# --- NEW: Login Form ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# --- NEW: Registration Form ---
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Custom validator to check if username is already taken
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # Custom validator to check if email is already in use
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class ManualProjectorForm(FlaskForm):
    income_goal = IntegerField('Annual Income Goal', 
                               validators=[DataRequired(), NumberRange(min=0)])
    days_to_forecast = IntegerField('Number of Days to Forecast', 
                                    validators=[DataRequired(), NumberRange(min=1)])
    doors_knocked = IntegerField('Historical: Total Doors Knocked', 
                                 validators=[DataRequired(), NumberRange(min=0)])
    appointments_set = IntegerField('Historical: Total Appointments Set', 
                                    validators=[DataRequired(), NumberRange(min=0)])
    deals_signed = IntegerField('Historical: Total Deals Signed', 
                                validators=[DataRequired(), NumberRange(min=0)])
    deals_completed = IntegerField('Historical: Total Deals Completed', 
                                   validators=[DataRequired(), NumberRange(min=0)])
    total_rcv = DecimalField('Historical: Total RCV from Completed Deals', 
                             validators=[DataRequired(), NumberRange(min=0)],
                             places=2)
    submit = SubmitField('Calculate Forecast')


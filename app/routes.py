# File: app/routes.py

# This file defines the URLs for our website and the logic that handles requests.

from flask import render_template, flash, redirect, url_for, request, abort
from app import app, db
from app.forms import LeadForm, DealForm, SettingsForm, DailyActivityForm, LoginForm, RegistrationForm
from app.models import Lead, Deal, Settings, DailyActivity, User
from datetime import date
from app.forms import LoginForm, RegistrationForm, LeadForm, DealForm, ManualProjectorForm
from decimal import Decimal
from sqlalchemy import func
from flask_login import login_user, logout_user, current_user, login_required

# --- User Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# --- Dashboard / Home Page ---
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    settings_form = SettingsForm()
    activity_form = DailyActivityForm()
    
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = Settings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()

    if 'submit_settings' in request.form and settings_form.validate_on_submit():
        settings.annual_income_goal = settings_form.annual_income_goal.data
        db.session.commit()
        flash('Your income goal has been updated!', 'success')
        return redirect(url_for('index'))

    if 'submit_activity' in request.form and activity_form.validate_on_submit():
        today_activity = DailyActivity.query.filter_by(date=date.today(), user_id=current_user.id).first()
        if not today_activity:
            today_activity = DailyActivity(
                date=date.today(),
                doors_knocked=activity_form.doors_knocked.data,
                appointments_set=activity_form.appointments_set.data,
                user_id=current_user.id
            )
            db.session.add(today_activity)
        else:
            today_activity.doors_knocked = activity_form.doors_knocked.data
            today_activity.appointments_set = activity_form.appointments_set.data
        db.session.commit()
        flash('Your daily activity has been logged!', 'success')
        return redirect(url_for('index'))

    today_activity = DailyActivity.query.filter_by(date=date.today(), user_id=current_user.id).first()

    if request.method == 'GET':
        settings_form.annual_income_goal.data = settings.annual_income_goal
        if today_activity:
            activity_form.doors_knocked.data = today_activity.doors_knocked
            activity_form.appointments_set.data = today_activity.appointments_set
        else:
            activity_form.doors_knocked.data = 0
            activity_form.appointments_set.data = 0
    
    leads = Lead.query.filter_by(user_id=current_user.id).all()
    deals = Deal.query.join(Lead).filter(Lead.user_id == current_user.id).all()
    
    pipeline_value = sum(d.contract_price for d in deals if d.status != 'Job Completed')
    potential_commission = sum(d.contract_price * (d.commission_rate / 100) for d in deals if d.status != 'Job Completed')
    earned_commission = sum(d.contract_price * (d.commission_rate / 100) for d in deals if d.status == 'Job Completed')

    total_doors_knocked = db.session.query(func.sum(DailyActivity.doors_knocked)).filter_by(user_id=current_user.id).scalar() or 0
    total_appointments_set = db.session.query(func.sum(DailyActivity.appointments_set)).filter_by(user_id=current_user.id).scalar() or 0
    signed_deals = Deal.query.join(Lead).filter(Lead.user_id == current_user.id, Deal.status.in_(['Contract Signed', 'Job Completed'])).all()
    total_signed_deals = len(signed_deals)
    completed_deals = Deal.query.join(Lead).filter(
        Lead.user_id == current_user.id, 
        Deal.status == 'Job Completed'
    ).all()
    completed_deals_count = len(completed_deals)

    # Calculate the historical completion rate
    completion_rate = completed_deals_count / total_signed_deals if total_signed_deals > 0 else 0
    
    # Calculate avg commission based ONLY on completed deals
    avg_commission_per_deal = (sum(d.contract_price * (d.commission_rate / 100) for d in completed_deals)) / completed_deals_count if completed_deals_count > 0 else 0
    doors_per_appointment = total_doors_knocked / total_appointments_set if total_appointments_set > 0 else 0
    appointments_per_deal = total_appointments_set / total_signed_deals if total_signed_deals > 0 else 0

    work_days_per_year = 250
    remaining_commission_goal = settings.annual_income_goal - earned_commission
    remaining_commission_goal = max(0, remaining_commission_goal)

    deals_needed = (remaining_commission_goal / avg_commission_per_deal) / completion_rate if avg_commission_per_deal > 0 and completion_rate > 0 else 0
    appointments_needed = deals_needed * appointments_per_deal
    doors_needed_total = appointments_needed * doors_per_appointment

    daily_appointments_goal = appointments_needed / work_days_per_year if work_days_per_year > 0 else 0
    daily_doors_goal = doors_needed_total / work_days_per_year if work_days_per_year > 0 else 0

    projections = {
        'avg_commission': avg_commission_per_deal, 'doors_per_appointment': doors_per_appointment,
        'appointments_per_deal': appointments_per_deal, 'deals_needed': deals_needed,
        'daily_appointments_goal': daily_appointments_goal, 'daily_doors_goal': daily_doors_goal,
        'completion_rate': completion_rate
    }

    return render_template('index.html', title='Dashboard', leads=leads, 
                           pipeline_value=pipeline_value, potential_commission=potential_commission, 
                           earned_commission=earned_commission, settings_form=settings_form,
                           activity_form=activity_form, annual_income_goal=settings.annual_income_goal,
                           projections=projections)

# --- Lead Management ---
@app.route('/add_lead', methods=['GET', 'POST'])
@login_required
def add_lead():
    form = LeadForm()
    if form.validate_on_submit():
        lead = Lead(
            first_name=form.first_name.data, last_name=form.last_name.data,
            phone_number=form.phone_number.data, email=form.email.data,
            address=form.address.data, notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(lead)
        db.session.commit()
        flash(f'Lead for {lead.first_name} {lead.last_name} created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_lead.html', title='Add New Lead', form=form)

@app.route('/lead/<int:lead_id>')
@login_required
def lead_detail(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)
    return render_template('lead_detail.html', title=f'Lead: {lead.first_name}', lead=lead)

@app.route('/lead/delete/<int:lead_id>', methods=['POST'])
@login_required
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)
    lead_name = f"{lead.first_name} {lead.last_name}"
    db.session.delete(lead)
    db.session.commit()
    flash(f'Lead for {lead_name} has been deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/lead/edit/<int:lead_id>', methods=['GET', 'POST'])
@login_required
def edit_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)
    form = LeadForm()
    if form.validate_on_submit():
        lead.first_name = form.first_name.data
        lead.last_name = form.last_name.data
        lead.phone_number = form.phone_number.data
        lead.email = form.email.data
        lead.address = form.address.data
        lead.notes = form.notes.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('lead_detail', lead_id=lead.id))
    elif request.method == 'GET':
        form.first_name.data = lead.first_name
        form.last_name.data = lead.last_name
        form.phone_number.data = lead.phone_number
        form.email.data = lead.email
        form.address.data = lead.address
        form.notes.data = lead.notes
    return render_template('edit_lead.html', title='Edit Lead', form=form, lead=lead)

# --- Deal Management ---
@app.route('/lead/<int:lead_id>/add_deal', methods=['GET', 'POST'])
@login_required
def add_deal(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)
    form = DealForm()
    if form.validate_on_submit():
        deal = Deal(
            status=form.status.data, contract_price=form.contract_price.data,
            commission_rate=form.commission_rate.data, lead_id=lead.id
        )
        db.session.add(deal)
        db.session.commit()
        flash(f'Deal created for {lead.first_name} {lead.last_name}!', 'success')
        return redirect(url_for('lead_detail', lead_id=lead.id))
    return render_template('add_deal.html', title='Add Deal', form=form, lead=lead)

@app.route('/deal/edit/<int:deal_id>', methods=['GET', 'POST'])
@login_required
def edit_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if deal.lead.user_id != current_user.id:
        abort(403)
    form = DealForm()
    if form.validate_on_submit():
        deal.status = form.status.data
        deal.contract_price = form.contract_price.data
        deal.commission_rate = form.commission_rate.data
        db.session.commit()
        flash('Deal information has been updated!', 'success')
        return redirect(url_for('lead_detail', lead_id=deal.lead_id))
    elif request.method == 'GET':
        form.status.data = deal.status
        form.contract_price.data = deal.contract_price
        form.commission_rate.data = deal.commission_rate
    return render_template('edit_deal.html', title='Edit Deal', form=form, deal=deal)

@app.route('/deal/delete/<int:deal_id>', methods=['POST'])
@login_required
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if deal.lead.user_id != current_user.id:
        abort(403)
    lead_id = deal.lead_id
    db.session.delete(deal)
    db.session.commit()
    flash('The deal has been deleted.', 'success')
    return redirect(url_for('lead_detail', lead_id=lead_id))

# File: app/routes.py

# File: app/routes.py

@app.route('/manual_projector', methods=['GET', 'POST'])
@login_required
def manual_projector():
    form = ManualProjectorForm()
    results = None  # Initialize results to None

    if form.validate_on_submit():
        # --- Safely get data from the form ---
        income_goal = form.income_goal.data
        days = form.days_to_forecast.data
        knocks = form.doors_knocked.data
        appts = form.appointments_set.data
        signs = form.deals_signed.data
        completes = form.deals_completed.data
        total_rcv = form.total_rcv.data

        try:
            # --- Calculate Historical Ratios (handle division by zero) ---
            avg_rcv = total_rcv / completes if completes > 0 else 0
            knock_to_appt_ratio = appts / knocks if knocks > 0 else 0
            appt_to_sign_ratio = signs / appts if appts > 0 else 0
            sign_to_complete_ratio = completes / signs if signs > 0 else 0

            # --- Calculate Commission and Target Deals ---
            # Using the user's settings for margin and commission rate
            avg_profit = avg_rcv * (Decimal(current_user.company_margin) / 100)
            commission_per_deal = avg_profit * (Decimal(current_user.commission_rate) / 100)
            
            target_deals_needed = income_goal / commission_per_deal if commission_per_deal > 0 else 0
            
            # --- Work Backwards to Find Daily Goals ---
            target_deals_per_day = target_deals_needed / days if days > 0 else 0
            
            target_signs_per_day = (Decimal(target_deals_per_day) / sign_to_complete_ratio) if sign_to_complete_ratio > 0 else 0
            target_appts_per_day = (Decimal(target_signs_per_day) / appt_to_sign_ratio) if appt_to_sign_ratio > 0 else 0
            target_knocks_per_day = (Decimal(target_appts_per_day) / knock_to_appt_ratio) if knock_to_appt_ratio > 0 else 0

            results = {
                'daily_knocks': target_knocks_per_day,
                'daily_appointments': target_appts_per_day,
                'daily_deals_signed': target_signs_per_day
            }

        except ZeroDivisionError:
            flash('Cannot calculate with zero values in historical data. Please enter valid numbers.', 'danger')
        
    return render_template('manual_projector.html', title='Manual Projector', form=form, results=results)


# File: app/routes.py

from datetime import date

from flask import (
    render_template, flash, redirect, url_for, request, abort, jsonify
)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import func

from app import app, db
from app.models import Lead, Deal, Settings, DailyActivity, User
from app.forms import (
    LoginForm, RegistrationForm,
    SettingsForm, DailyActivityForm,
    LeadForm, DealForm, ManualProjectorForm
)
from app.services.projector import Ratios, projector_metrics
from app.models import LEAD_STATUS_ORDER

SYNONYMS = {
    "Appointment Set": "Appt",
    "Contract Signed": "Signed",
    "Job Completed": "Completed",
}
def _norm(s): return SYNONYMS.get(s, s)

def _max_deal_status(lead):
    if not lead.deals:
        return lead.status
    inv = {v:k for k,v in LEAD_STATUS_ORDER.items()}
    top = max(LEAD_STATUS_ORDER.get(d.status, 0) for d in lead.deals)
    return inv.get(top, lead.status)

def _sync_lead_from_deals(lead):
    lead.status = _max_deal_status(lead)

# -----------------------------
# Auth
# -----------------------------
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


# -----------------------------
# Dashboard
# -----------------------------
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
        today_activity = DailyActivity.query.filter_by(
            date=date.today(), user_id=current_user.id
        ).first()
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

    # prefill GET
    today_activity = DailyActivity.query.filter_by(
        date=date.today(), user_id=current_user.id
    ).first()
    if request.method == 'GET':
        settings_form.annual_income_goal.data = settings.annual_income_goal
        if today_activity:
            activity_form.doors_knocked.data = today_activity.doors_knocked
            activity_form.appointments_set.data = today_activity.appointments_set
        else:
            activity_form.doors_knocked.data = 0
            activity_form.appointments_set.data = 0

    # Aggregates
    leads = Lead.query.filter_by(user_id=current_user.id).all()
    deals = Deal.query.join(Lead).filter(Lead.user_id == current_user.id).all()

    pipeline_value = sum(d.contract_price for d in deals if d.status != 'Job Completed')
    potential_commission = sum(
        d.contract_price * (d.commission_rate / 100) for d in deals
        if d.status != 'Job Completed'
    )
    earned_commission = sum(
        d.contract_price * (d.commission_rate / 100) for d in deals
        if d.status == 'Job Completed'
    )

    total_doors_knocked = db.session.query(
        func.sum(DailyActivity.doors_knocked)
    ).filter_by(user_id=current_user.id).scalar() or 0
    total_appointments_set = db.session.query(
        func.sum(DailyActivity.appointments_set)
    ).filter_by(user_id=current_user.id).scalar() or 0

    signed_deals = Deal.query.join(Lead).filter(
        Lead.user_id == current_user.id,
        Deal.status.in_(['Contract Signed', 'Job Completed'])
    ).all()
    total_signed_deals = len(signed_deals)

    completed_deals = Deal.query.join(Lead).filter(
        Lead.user_id == current_user.id,
        Deal.status == 'Job Completed'
    ).all()
    completed_deals_count = len(completed_deals)

    completion_rate = (
        completed_deals_count / total_signed_deals
        if total_signed_deals > 0 else 0
    )
    avg_commission_per_deal = (
        sum(d.contract_price * (d.commission_rate / 100) for d in completed_deals) /
        completed_deals_count
        if completed_deals_count > 0 else 0
    )
    doors_per_appointment = (
        total_doors_knocked / total_appointments_set
        if total_appointments_set > 0 else 0
    )
    appointments_per_deal = (
        total_appointments_set / total_signed_deals
        if total_signed_deals > 0 else 0
    )

    work_days_per_year = 250
    remaining_commission_goal = max(
        0, (settings.annual_income_goal or 0) - earned_commission
    )

    deals_needed = (
        (remaining_commission_goal / avg_commission_per_deal) / completion_rate
        if avg_commission_per_deal > 0 and completion_rate > 0 else 0
    )
    appointments_needed = deals_needed * appointments_per_deal
    doors_needed_total = appointments_needed * doors_per_appointment

    projections = {
        'avg_commission': avg_commission_per_deal,
        'doors_per_appointment': doors_per_appointment,
        'appointments_per_deal': appointments_per_deal,
        'deals_needed': deals_needed,
        'daily_appointments_goal': (appointments_needed / work_days_per_year) if work_days_per_year else 0,
        'daily_doors_goal': (doors_needed_total / work_days_per_year) if work_days_per_year else 0,
        'completion_rate': completion_rate
    }

    return render_template(
        'index.html',
        title='Dashboard',
        leads=leads,
        pipeline_value=pipeline_value,
        potential_commission=potential_commission,
        earned_commission=earned_commission,
        settings_form=settings_form,
        activity_form=activity_form,
        annual_income_goal=settings.annual_income_goal,
        projections=projections
    )


# -----------------------------
# Leads
# -----------------------------
@app.route('/add_lead', methods=['GET', 'POST'])
@login_required
def add_lead():
    form = LeadForm()
    if form.validate_on_submit():
        lead = Lead(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            notes=form.notes.data,
            user_id=current_user.id,  # Lead.status uses model default
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
    """Edit all lead fields, including status."""
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)

    form = LeadForm(obj=lead)

    if request.method == 'POST':
        if not form.validate_on_submit():
            flash(f"Form errors: {form.errors}", "danger")
            return render_template('edit_lead.html', title='Edit Lead', form=form, lead=lead)

        before = lead.status
        new_status = _norm(form.status.data)

        lead.first_name   = form.first_name.data
        lead.last_name    = form.last_name.data
        lead.phone_number = form.phone_number.data
        lead.email        = form.email.data
        lead.address      = form.address.data
        lead.notes        = form.notes.data
        lead.status       = new_status

        # push lead status down to every existing deal
        for d in lead.deals:
            d.status = new_status

        db.session.commit()
        flash(f"Lead saved. Status: {before} → {lead.status} (applied to {len(lead.deals)} deal(s))", "success")
        return redirect(url_for('lead_detail', lead_id=lead.id))
    return render_template('edit_lead.html', title='Edit Lead', form=form, lead=lead)

# -----------------------------
# Deals
# -----------------------------
def _ensure_contract_price_if_completed(form):
    """Attach a validation error if status is Job Completed but price is empty/nonpositive."""
    if (form.status.data == 'Job Completed') and (not form.contract_price.data or form.contract_price.data <= 0):
        form.contract_price.errors.append('Contract price is required for completed jobs.')
        return False
    return True


@app.route('/lead/<int:lead_id>/add_deal', methods=['GET', 'POST'])
@login_required
def add_deal(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if lead.user_id != current_user.id:
        abort(403)

    form = DealForm()

    # Prefill defaults on GET
    if request.method == 'GET':
        if form.commission_base.data is None:
            form.commission_base.data = 'profit'
        if form.company_margin.data is None:
            form.company_margin.data = current_user.company_margin or 30.0
        if form.commission_rate.data is None:
            form.commission_rate.data = current_user.commission_rate or 40.0

    if form.validate_on_submit():
        if not _ensure_contract_price_if_completed(form):
            return render_template('add_deal.html', title='Add Deal', form=form, lead=lead)

        deal = Deal(
            status=form.status.data,
            contract_price=form.contract_price.data or 0.0,
            commission_rate=form.commission_rate.data,
            commission_base=form.commission_base.data,
            company_margin=form.company_margin.data or 0.0,
            lead_id=lead.id,
        )
        db.session.add(deal)
        db.session.commit()
        # keep lead.status in sync with its deals
        _sync_lead_from_deals(lead)
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

    if request.method == 'GET':
        form.status.data = deal.status
        form.contract_price.data = deal.contract_price
        form.commission_rate.data = deal.commission_rate
        form.commission_base.data = deal.commission_base or 'profit'
        form.company_margin.data = deal.company_margin if (deal.commission_base or 'profit') == 'profit' else 0.0

    if form.validate_on_submit():
        if not _ensure_contract_price_if_completed(form):
            return render_template('edit_deal.html', title='Edit Deal', form=form, deal=deal)

        deal.status = form.status.data
        deal.contract_price = form.contract_price.data or 0.0
        deal.commission_rate = form.commission_rate.data
        deal.commission_base = form.commission_base.data
        deal.company_margin = form.company_margin.data or 0.0
        db.session.commit()
        lead = deal.lead
        _sync_lead_from_deals(lead)
        db.session.commit()

        flash('Deal information has been updated!', 'success')
        return redirect(url_for('lead_detail', lead_id=deal.lead_id))

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


# -----------------------------
# Manual projector (UI + JSON)
# -----------------------------
@app.route('/manual_projector', methods=['GET', 'POST'])
@login_required
def manual_projector():
    form = ManualProjectorForm()
    results, error = None, None

    if form.validate_on_submit():
        income_goal = float(form.income_goal.data or 0)
        days        = int(form.days_to_forecast.data or 0)
        knocks      = int(form.doors_knocked.data or 0)
        appts       = int(form.appointments_set.data or 0)
        signs       = int(form.deals_signed.data or 0)
        completes   = int(form.deals_completed.data or 0)
        total_rcv   = float(form.total_rcv.data or 0)

        try:
            if days <= 0:
                raise ValueError("Days must be > 0.")
            if appts <= 0 or signs <= 0 or completes <= 0 or total_rcv <= 0:
                raise ValueError("Historical totals must be > 0.")

            ratios = Ratios(
                doors_per_appt = knocks / appts,
                appts_per_deal = appts / signs,
                avg_rcv_per_completed_deal = total_rcv / completes,
            )

            commission_base = (request.form.get('commission_base') or 'profit').strip()
            commission_pct  = float((request.form.get('commission_rate') or current_user.commission_rate or 0))
            company_margin  = float((request.form.get('company_margin') or current_user.company_margin or 0))

            metrics = projector_metrics(
                annual_goal=income_goal,
                days=days,
                ratios=ratios,
                commission_pct=commission_pct,
                company_margin_pct=company_margin,
                commission_base=commission_base,
            )

            sign_to_complete_ratio = completes / signs
            if sign_to_complete_ratio <= 0:
                raise ValueError("Invalid sign→complete ratio.")

            deals_signed_per_day = metrics["deals_per_day"] / sign_to_complete_ratio
            appts_per_day        = deals_signed_per_day * ratios.appts_per_deal
            doors_per_day        = appts_per_day * ratios.doors_per_appt

            results = {
                "daily_knocks":       doors_per_day,
                "daily_appointments": appts_per_day,
                "daily_deals_signed": deals_signed_per_day,
                "assumptions": {
                    "commission_base": commission_base,
                    "company_margin_pct": company_margin if commission_base == "profit" else 0.0,
                    "commission_pct": commission_pct,
                },
                "ratios": {
                    "doors_per_appt": ratios.doors_per_appt,
                    "appts_per_deal": ratios.appts_per_deal,
                    "avg_rcv_per_completed_deal": ratios.avg_rcv_per_completed_deal,
                },
                "percents": {
                    "door_to_appt": (appts / knocks * 100.0) if knocks > 0 else 0.0,
                    "appt_to_sign": (signs / appts * 100.0) if appts  > 0 else 0.0,
                    "sign_to_complete": (completes / signs * 100.0) if signs > 0 else 0.0,
                    "effective_on_revenue": metrics["eff_rate"] * 100.0,
                },
                "avg_comm_per_deal": metrics["avg_comm_per_deal"],
            }

        except Exception as e:
            error = str(e)

    return render_template(
        "manual_projector.html",
        title="Manual Projector",
        form=form,
        results=results,
        error=error,
    )


@app.route('/manual_projector.json', methods=['GET', 'POST'])
@login_required
def manual_projector_json():
    data = request.get_json(force=True) if request.method == 'POST' else {}

    income_goal = float(data.get('income_goal', 0))
    days = int(data.get('days_to_forecast', 0))
    knocks = int(data.get('doors_knocked', 0))
    appts = int(data.get('appointments_set', 0))
    signs = int(data.get('deals_signed', 0))
    completes = int(data.get('deals_completed', 0))
    total_rcv = float(data.get('total_rcv', 0))
    commission_base = (data.get('commission_base') or 'profit').strip()
    commission_pct  = float(data.get('commission_rate', current_user.commission_rate or 0))
    company_margin  = float(data.get('company_margin', current_user.company_margin or 0))

    if days <= 0 or appts <= 0 or signs <= 0 or completes <= 0 or total_rcv <= 0:
        return jsonify({"error": "All inputs must be > 0"}), 400

    ratios = Ratios(
        doors_per_appt = knocks / appts,
        appts_per_deal = appts / signs,
        avg_rcv_per_completed_deal = total_rcv / completes,
    )
    metrics = projector_metrics(
        annual_goal=income_goal,
        days=days,
        ratios=ratios,
        commission_pct=commission_pct,
        company_margin_pct=company_margin,
        commission_base=commission_base,
    )

    sign_to_complete_ratio = completes / signs
    deals_signed_per_day = metrics["deals_per_day"] / sign_to_complete_ratio
    appts_per_day  = deals_signed_per_day * ratios.appts_per_deal
    doors_per_day  = appts_per_day * ratios.doors_per_appt

    return jsonify({
        "deals_per_day": deals_signed_per_day,
        "appts_per_day": appts_per_day,
        "doors_per_day": doors_per_day,
        "assumptions": {
            "commission_base": commission_base,
            "company_margin_pct": company_margin if commission_base == "profit" else 0.0,
            "commission_pct": commission_pct,
        },
        "percents": {
            "door_to_appt": (appts / knocks * 100.0) if knocks > 0 else 0.0,
            "appt_to_sign": (signs / appts * 100.0),
            "sign_to_complete": (completes / signs * 100.0),
            "effective_on_revenue": metrics["eff_rate"] * 100.0,
        },
        "avg_comm_per_deal": metrics["avg_comm_per_deal"],
        "ratios": {"avg_rcv_per_completed_deal": ratios.avg_rcv_per_completed_deal},
    })


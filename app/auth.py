from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db, login_manager
from flask_login import login_user, login_required, logout_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        username = request.form.get('username','').strip()
        password = request.form['password']
        interests = request.form.get('interests','')
        if User.query.filter_by(email=email).first():
            flash('Email already exists','danger'); return redirect(url_for('auth.register'))
        u = User(email=email, username=username, interests=interests)
        u.set_password(password)
        db.session.add(u); db.session.commit()
        flash('Account created. Login now.','success'); return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        pw = request.form['password']
        u = User.query.filter_by(email=email).first()
        if u and u.check_password(pw):
            login_user(u)
            
            # NEW: Update daily login and gamification
            login_success, login_data = u.update_daily_login()
            
            if login_success and isinstance(login_data, dict):
                # Flash gamification messages
                if login_data['streak_bonus'] > 0:
                    flash(f'🔥 {login_data["current_streak"]} day streak! Bonus: +{login_data["streak_bonus"]} XP!', 'success')
                else:
                    flash(f'📈 Daily login: +{login_data["daily_xp"]} XP! Streak: {login_data["current_streak"]} days', 'success')
            
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials','danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out','info')
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

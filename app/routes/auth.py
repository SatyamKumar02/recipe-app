from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, SignupForm
from app.models import User
from werkzeug.security import generate_password_hash
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if user already exists
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create new user
        hashed_pw = generate_password_hash(password)
        db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_pw
        })

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(db, form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('views.recipes'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

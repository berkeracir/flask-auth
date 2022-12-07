from flask import Blueprint, render_template, redirect, url_for, request, flash, Markup
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
	return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = bool(request.form.get('remember'))

	user = User.query.filter_by(email=email).first()

	# check if the user actually exists and if user exists, take the user-supplied password, hash it, and compare it to the hashed password in the database
	if not user or not check_password_hash(user.password, password):
		flash('Invalid email or password!')
		return redirect(url_for('auth.login'))	# if the user doesn't exist or password is wrong, reload the page

	# if the above check passes, then we know the user has the right credentials
	login_user(user, remember=remember)
	return redirect(url_for('main.lists'))

@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
	# validate and add user to database
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')

	if not email:	# if email field is empty, redirect back to signup page so user can try again
		flash("Email cannot be empty!")
		return redirect(url_for('auth.signup'))	# TODO: redirecting to same page with already filled form data woud be better

	user = User.query.filter_by(email=email).first()	# if this returns a user, then the email already exists in database

	if user:	# if a user is found, redirect back to signup page so user can try again
		flash(Markup(f"Email has already taken! Go to <a href=\"{url_for('auth.login')}\">login page</a>."))
		return redirect(url_for('auth.signup'))	# TODO: redirecting to same page with already filled form data woud be better
	
	if not name:	# if name field is empty, redirect back to signup page so user can try again
		flash("Name cannot be empty!")
		return redirect(url_for('auth.signup'))	# TODO: redirecting to same page with already filled form data woud be better

	# create a new user with the form data. Hash the password so the plaintext version isn't saved.
	new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

	# add the new user to the database
	db.session.add(new_user)
	db.session.commit()

	return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))
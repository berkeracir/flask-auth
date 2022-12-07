from flask import Blueprint, render_template, request, redirect, url_for, flash, Markup
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', user=current_user)

@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
	# update user information
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')
	new_password = request.form.get('new_password')

	# check the user-supplied password, hash it, and compare it to the hashed password in the database
	if not check_password_hash(current_user.password, password):
		flash('Invalid password!')
		return redirect(url_for('main.profile'))	# if password is wrong, reload the page
	
	if not name:	# if name field is empty, redirect back to signup page so user can try again
		flash("Name cannot be empty!")
		return redirect(url_for('main.profile'))	# TODO: redirecting to same page with already filled form data woud be better

	# update the existing user with new name or new password. Hash the password so the plaintext version isn't saved.
	if new_password:
		current_user.password = generate_password_hash(new_password, method='sha256')
	current_user.name = name

	# update the existing user to the database
	db.session.add(current_user)
	db.session.commit()

	return redirect(url_for('main.lists'))

@main.route('/lists')
@login_required
def lists():
	return render_template('lists.html', user=current_user)
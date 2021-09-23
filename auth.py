import functools
import datetime

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
bp = Blueprint('auth', __name__, url_prefix='/auth')

from .database import database_session
from .models import User, Account

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		password2 = request.form['password2']
		email = request.form['email']
		discord = request.form['discord']
		other = request.form['other']

		error = None
		if password != password2:
			error = 'The passwords are not identical. Please retype.'

		if not username:
			error = 'Username is required.'
		if not password:
			error = 'Password is required.'
		
		# Check if username is already registered.
		if database_session.query(User.username).filter_by(username=username).first() is not None:
			error = "This username was already taken by somenoe else. Please choose another."

		# Register the user.
		if email == "": email = None
		if discord == "": discord = None
		if other == "": other = None

		if error is None:
			user = User(
				username=username,
				password=generate_password_hash(password),
				email=email,
				discord=discord,
				other=other,
				email_validated=False,
				discord_validated=False,
				deleted=False,
				creation_time=round(datetime.datetime.utcnow().timestamp()),
				time_zone=0
			)
			
			database_session.add(user)
			database_session.commit()
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		# Search for the user.
		error = None
		user = database_session.query(User).filter_by(username=username).first()

		# Check if these are correct, of course.
		if user is None:
			error = 'Incorrect username or password'
		elif not check_password_hash(user.password, password):
			error = 'Incorrect username or password'
		
		# Log in.
		if error is None:
			# Logs the user in.
			session.clear()
			session['user_id'] = user.id

			# If user has no accounts, direct him for account creation. :).
			# If user has no worlds, and just a single account, direct him there.
			# If user has several accounts, direct him to account list.
			# If a user owns worlds, direct to a nicer user page.

			account_data = database_session.query(Account).filter(Account.user_id == user.id).all()
			if len(account_data) == 1:
				return redirect(url_for('account.view', acc_number=account_data[0].acc_number))
			else:
				return redirect(url_for('user.view'))


		flash(error)
	
	return render_template('auth/login.html')	


@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('world.list'))


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = database_session.query(User.username).filter(User.id == user_id).first()


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)
	
	return wrapped_view

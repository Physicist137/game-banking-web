import datetime
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('user', __name__, url_prefix='/user')

from .database import database_session
from .models import User, Account, World
from .helper import get_several_accounts_info

from sqlalchemy import or_


@bp.route('/view', methods=('GET', 'POST'))
def view():
	# Check if user is logged in.
	user_id = session['user_id']
	if user_id is None: return redirect(url_for('auth.login'))

	# Check if logged in user really exists.
	user = database_session.query(User).filter(User.id == user_id).first()
	if user is None: return redirect(url_for('auth.login'))

	# Get information accounts.
	data_accounts_number = database_session.query(Account.acc_number).filter(Account.user_id == user_id).all()
	number_array = []
	for data in data_accounts_number:
		number_array.append(int(data[0]))

	accounts = get_several_accounts_info(number_array)

	# Verify if the user has any account.
	if data_accounts_number == None: has_accounts = False
	else: has_accounts = True

	# Check if these accounts are single world or not.
	single_world = True
	if has_accounts == True:
		for account in accounts:
			if account['world'] != accounts[0]['world']:
				single_world = False
				break


	# Check worlds owned by the player.
	worlds = []
	data_worlds = database_session.query(World).filter(World.owner_id == user_id).all()
	for data in data_worlds:
		world = dict()
		world['id'] = data.id
		world['private'] = data.private
		world['name'] = data.name
		worlds.append(world)

	if len(worlds) == 0: has_worlds = False
	else: has_worlds = True

	# Render the template.
	return render_template('user/view.html',
		username=user.username,
		accounts=accounts,
		worlds=worlds,
		single_world=single_world,
		has_worlds=has_worlds
	)

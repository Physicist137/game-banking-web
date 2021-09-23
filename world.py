import datetime
import hashlib

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

bp = Blueprint('world', __name__, url_prefix='/world')


from .auth import login_required
from .database import database_session
from .models import User, World, Currency, Account, Link, CurrencyWorld
from .helper import get_several_accounts_info
from .vars import Global



@bp.route('/list', methods=('GET', 'POST'))
def list():
	data_worlds = database_session.query(World).filter(World.private == False).order_by(World.id).all()

	worlds = []
	for data in data_worlds:
		world = dict()
		world['id'] = data.id
		world['name'] = data.name
		world['desc'] = data.short_description
		worlds.append(world)

	return render_template('world/list.html', worlds=worlds)


@login_required
@bp.route('/create', methods=('GET', 'POST'))
def create():
	if request.method == 'POST':
		user_id = session['user_id']
		error = None

		# Process worldname.
		name = request.form['name']
		if name == "" or name == None:
			error = "Name of the world is empty! Please fill out."

		# Process visibility.
		if request.form['visibility'] == 'public':
			private = False
		else:
			private = True
		
		
		# Process account maximum.
		mm = request.form['max_acc']
		if mm == "": max_account_per_user = -1
		else:
			try: max_account_per_user = int(mm)
			except: error = "Invalid number of accounts an user can make! Please fix it!"

		# Process short description
		short_description = request.form['short']
		if short_description == "": short_description = None

		# Process long description
		long_description = request.form['short']
		if long_description == "": long_description = None

		# Get the ID of the main currency.
		comma_separated = request.form['currencies'].replace(" ", "").upper()
		currencies_iso = request.form['currencies'].split(",")

		# Verify if the currencies exist, and if yes, append to currency.
		currencies_id = []
		for iso in currencies_iso:
			currency_data = database_session.query(Currency).filter(Currency.iso == iso).first()
			if currency_data is not None: currencies_id.append(currency_data.id)

		# Verify if currencies checked.
		if len(currencies_id) == 0:
			error = "No currencies could be processed. Please write the correct ISO codes for them"

		# Finally save in the database.
		if error is None:
			creation_time = round(datetime.datetime.utcnow().timestamp())
			world = World(
				owner_id=user_id,
				deleted=False,
				creation_time=creation_time,
				private=private,
				max_account_per_user=max_account_per_user,
				name=name,
				short_description=short_description,
				long_description=long_description
			)
			database_session.add(world)
			database_session.flush()

			# Add currencies.			
			for currency_id in currencies_id:
				currencyworld = CurrencyWorld(
					world_id=world.id,
					currency_id=currency_id,
					creation_time=creation_time
				)
				database_session.add(currencyworld)
				database_session.flush()

			# Create a central account.
			acc_number = 500 + database_session.query(Account).count()
			account = Account(
				world_id=world.id,
				user_id=user_id,
				acc_number=acc_number,
				acc_type=Account.Type.central,
				deleted=False,
				creation_time=creation_time,
			)
			database_session.add(account)
			database_session.flush()			

			# Commit all changes into the database
			database_session.commit()
			return redirect(url_for('world.list'))


		# There were an error. Flash it.
		flash(error)

	
	# Didn't receive post request. Render page.
	return render_template('world/create.html')


@bp.route('/manage/<int:world_id>', methods=('GET', 'POST'))
def manage(world_id):
	# Check if the user is logged in.
	user_id = session['user_id']
	if user_id is None: return redirect(url_for('auth.login'))

	# Check if the logged user does indeed exist.
	user = database_session.query(User).filter(User.id == user_id).first()
	if user is None: return redirect(url_for('auth.login'))

	# Load from database.
	data_accounts_number = database_session.query(Account.acc_number).filter(Account.world_id == world_id).all()
	data = database_session.query(World).filter(World.id == world_id).first()

	# Check if user can manage the world (if he's the owner).
	if (data.owner_id != user_id): abort(403)
	
	# Prepare data.
	world = dict()
	world['id'] = data.id
	world['private'] = data.private
	world['name'] = data.name
	world['short_description'] = data.short_description
	world['long_description'] = data.long_description

	# Get currencies info.
	currencies = []
	data_currency_world = database_session.query(CurrencyWorld).filter(CurrencyWorld.world_id == world_id).all()
	for data in data_currency_world:
		currency = dict()
		data_currency = database_session.query(Currency).filter(Currency.id == data.currency_id).first()
		currency['id'] = data_currency.id
		currency['iso'] = data_currency.iso
		currency['where'] = data_currency.from_where
		currency['name'] = data_currency.names
		currencies.append(currency)	

	
	number_array = []
	for data in data_accounts_number:
		number_array.append(int(data[0]))

	accounts = get_several_accounts_info(number_array)
	return render_template('world/manage.html', 
		username=user.username,
		world=world,
		accounts=accounts,
		currencies=currencies
	)
	
	# Delete world.
	# Create deposit/central account.
	# Create invite links.	
	# Modify public/private.
	# Show the list of accounts, and their balances.


@bp.route('/manage/link/<int:world_id>', methods=('GET', 'POST'))
def manage_link(world_id):
	# Check if the user is logged in.
	user_id = session['user_id']
	if user_id is None: return redirect(url_for('auth.login'))

	# Check if the logged user does indeed exist.
	user = database_session.query(User).filter(User.id == user_id).first()
	if user is None: return redirect(url_for('auth.login'))

	# Check if user can manage the world (if he's the owner).
	data_world = database_session.query(World).filter(World.id == world_id).first()
	if (data_world.owner_id != user_id): abort(403)

	# Process any link creation request.
	if request.method == 'POST':
		# Prepare to generate the link.
		amount = database_session.query(Link).count()
		salt = "this_is_a_nice_salt_that_perhaps_Ill_change_later"
		rand = "fn65dg41z3 gv41s<53"
	
		# Generate the link	
		string = str(amount) + salt + str(amount) + rand + str(amount)
		byte_string = string.encode()
		m = hashlib.sha256()
		m.update(byte_string)
		linkurl = m.hexdigest()
			
		# Save the link.
		link = Link(
			world_id=world_id,
			creation_date=round(datetime.datetime.utcnow().timestamp()),
			expire_date=-1,
			status=Link.Status.active,
			link=linkurl
		)

		database_session.add(link)
		database_session.commit()

		
	# Prepare data.
	world = dict()
	world['id'] = data_world.id
	world['name'] = data_world.name
	world['short_description'] = data_world.short_description
	world['long_description'] = data_world.long_description

	# Get the links.
	data_links = database_session.query(Link).filter(Link.world_id == world_id).order_by(Link.creation_date).all()
	reversed_data_links = data_links[::-1]
	links = []
	for data in reversed_data_links:
		link = dict()
		link['creation_date'] = datetime.datetime.fromtimestamp(data.creation_date).isoformat()
		
		if data.expire_date == -1:
			link['expire_date'] = "Unlimited"
		else:
			link['expire_date'] = datetime.datetime.fromtimestamp(data.expire_date).isoformat()

		if data.status == Link.Status.active:
			link['status'] = "<b><font color='green'>active</color></b>"
		elif data.status == Link.Status.disabled:
			link['status'] = "<b><font color='red'>disabled</color></b>"
		else:
			link['status'] = "<b><font color='black'>unknown</color></b>"

		link['link'] = Global.public_url + '/link/' + data.link
		links.append(link)

	# Render template.
	return render_template('world/manage_links.html',
		username=user.username,
		world=world,
		links=links
	)
	


@bp.route('/view/<int:world_id>', methods=('GET', 'POST'))
def view(world_id):
	# Load the user.
	if 'user_id' in session:
		user_id = session['user_id']
	else:
		user_id = None

	# Acquire data of the world.
	data_world = database_session.query(World).filter(World.id == world_id).first()
	
	# Check if the world is deleted.
	if (data_world.deleted == True): abort(404)

	# Check if the world is private
	if (data_world.private == True):
		# Check if one came from a link.
		valid_link = False
		if 'link' in session:
			linkurl = session['link']
			data_link = database_session.query(Link).filter(Link.link == linkurl).first()
			if data_link is not None: valid_link = True


		# If it didn't came from a valid link	
		if not valid_link:
			# Check if a user is logged in.
			if user_id is None:
				abort(404)

			# Check if the logged user can see the world.
			data_account = database_session.query(Account) \
				.filter(World.id == world_id) \
				.filter(Account.user_id == user_id) \
				.first()

			if (data_account == None):
				abort(404)


	# Prepare data.
	world = dict()
	world['id'] = data_world.id
	world['name'] = data_world.name
	world['short_description'] = data_world.short_description
	world['long_description'] = data_world.long_description

	# Render it
	return render_template('world/view.html', world=world)

	
		

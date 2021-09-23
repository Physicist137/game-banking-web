import datetime
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

bp = Blueprint('account', __name__, url_prefix='/account')

from .database import database_session
from .models import User, Account, Movement, World, Currency, CurrencyWorld
from .helper import get_account_info, html_balance
from .banking import transfer_operation
from .money import Money

from sqlalchemy import or_


@bp.route('/view/<int:acc_number>', methods=('GET', 'POST'))
def view(acc_number):
	if 'user_id' not in session:
		return redirect(url_for('auth.login'))

	user_id = session['user_id']

	# Get account information.
	account = database_session.query(Account).filter(Account.acc_number == acc_number).first()

	# If account is non existant, then don't.
	if (account == None): abort(403)

	# If a user does not belong to this account, then don't.
	if (user_id != account.user_id): abort(403)

	# Find type.
	if (account.acc_type == Account.Type.deposit):
		acc_type = 'Deposit'
	elif (account.acc_type == Account.Type.central):
		acc_type = 'Central'

	# Get all movements from this account	
	data_movements = database_session.query(Movement) \
		.filter(Movement.account_id == account.id) \
		.order_by(Movement.processed_time.desc()).all()

	# Gather all currencies used.
	currencies = []
	for data in data_movements:
		if data.currency_id not in currencies:
			currencies.append(data.currency_id)

	single_currency = (len(currencies) == 1)

	# Filter between concluded status only.
	movements = []
	if single_currency:
		currency_data = database_session.query(Currency).filter(Currency.id == currencies[0]).first()
		def from_value_to_html(balance):
			if currency_data.prefix != "":
				text_balance = Money(balance, currency_data.exponent).string(prefix=currency_data.prefix+' ')
			elif currency_data.posfix != "":
				text_balance = Money(balance, currency_data.exponent).string(suffix=' ' + currency_data.posfix)
			else:
				text_balance = Money(balance, currency_data.exponent).string(prefix=currency_data.iso + ' ')

			return html_balance(balance, text_balance)

		for data in data_movements:
			movement = dict()
			movement['value'] = from_value_to_html(data.value)
			movement['balance'] = from_value_to_html(data.balance)
			movement['date'] = datetime.datetime.fromtimestamp(data.processed_time).isoformat()
			movement['desc'] = data.short_description
			movements.append(movement)

	else:
		for data in data_movements:
			currency_data = database_session.query(Currency).filter(Currency.id == data.currency_id).first()
			def from_value_to_html(balance):
				if currency_data.prefix != "":
					text_balance = Money(balance, currency_data.exponent).string(prefix=currency_data.prefix+' ')
				elif currency_data.posfix != "":
					text_balance = Money(balance, currency_data.exponent).string(suffix=' ' + currency_data.posfix)
				else:
					text_balance = Money(balance, currency_data.exponent).string(prefix=currency_data.iso + ' ')
	
				return html_balance(balance, text_balance)

			movement = dict()
			movement['value'] = from_value_to_html(data.value)
			movement['balance'] = from_value_to_html(data.balance)
			movement['date'] = datetime.datetime.fromtimestamp(data.processed_time).isoformat()
			movement['desc'] = data.short_description
			movements.append(movement)

	# Render the template.
	return render_template('account/view.html', 
		account_number=acc_number,
		account_type=acc_type,
		movements=movements
	)


@bp.route('/create/<int:world_id>', methods=('GET', 'POST'))
def create(world_id):
	if 'user_id' not in session:
		return redirect(url_for('auth.login'))

	user_id = session['user_id']
	acc_number = 500 + database_session.query(Account).count()
	account = Account(
		world_id=world_id,
		user_id=user_id,
		acc_number=acc_number,
		acc_type=Account.Type.deposit,
		deleted=False,
		creation_time=round(datetime.datetime.utcnow().timestamp())
	)

	database_session.add(account)
	database_session.commit()

	return redirect(url_for('account.view', acc_number=acc_number))



@bp.route('/central/<int:world_id>', methods=('GET', 'POST'))
def central(world_id):
	acc_number = database_session.query(Account.acc_number) \
		.filter(Account.world_id == world_id) \
		.filter(Account.acc_type == Account.Type.central).first()[0]

	return redirect(url_for('account.transfer', acc_number=acc_number))


@bp.route('/transfer/<int:acc_number>', methods=('GET', 'POST'))
def transfer(acc_number):
	if 'user_id' not in session:
		return redirect(url_for('auth.login'))

	user_id = session['user_id']
	error = None

	# Get information about the account.
	account_info = get_account_info(acc_number)

	# Verify if there is only a single currency.
	single_currency = (len(account_info['last_movement']) <= 1)
	no_movements = (len(account_info['last_movement']) == 0)

	# Get account information.
	if account_info['acc_type'] == Account.Type.deposit: acc_type = 'deposit'
	elif account_info['acc_type'] == Account.Type.central: acc_type = 'central'
	else: acc_type = 'unknown'

	# Get all currencies the user has, if it is a deposit account.
	currencies = []
	if account_info['acc_type'] == Account.Type.deposit:
		for last in account_info['last_movement']:
			currency = dict()
			currency['id'] = last['currency']['id']
			currency['exponent'] = last['currency']['exponent']
			currency['html'] = last['currency']['iso'] + ' - ' + last['currency']['name']
			currencies.append(currency)


	# Get all currencies the world has, if it is a central account.
	elif account_info['acc_type'] == Account.Type.central:
		world_currency_data = database_session.query(CurrencyWorld) \
			.filter(CurrencyWorld.world_id == account_info['world']['id']).all()

		if world_currency_data == None: pass
		elif len(world_currency_data) == 1:
			single_currency = True
			currency_data = database_session.query(Currency).filter(Currency.id == world_currency_data[0].currency_id).first()
			currency = dict()
			currency['id'] = currency_data.id
			currency['exponent'] = currency_data.exponent
			currency['html'] = currency_data.iso + ' - ' + currency_data.names
			currencies.append(currency)
		else:
			single_currency = False
			for data in world_currency_data:
				currency_data = database_session.query(Currency).filter(Currency.id == data.currency_id).first()
				currency = dict()
				currency['id'] = currency_data.id
				currency['exponent'] = currency_data.exponent
				currency['html'] = '[' + currency_data.iso + '] ' + currency_data.names 
				currencies.append(currency)
			
			

	# Process a transfer request.
	if request.method == 'POST':
		# Request transfer data.
		try: amount = float(request.form['value'])
		except: error = "Unable to process the amount of money to transfer"

		try: to_account_number = int(request.form['to_account'])
		except: error = "Unable to process the account to transfer the money"

		desc = request.form['description']

		# Read accounts.
		if error is None:
			to_account = database_session.query(Account).filter(Account.acc_number == to_account_number).first()
			from_account = database_session.query(Account).filter(Account.acc_number == acc_number).first()

			if to_account == None:
				error = "Transfer could not be processed. Invalid recipient account"

			if acc_number == to_account_number:
				error = "You cannot make a transfer from this account to this same account"

			# Verify if they are in equal worlds.
			to_world = database_session.query(World).filter(World.id == to_account.world_id).first()
			from_world = database_session.query(World).filter(World.id == from_account.world_id).first()
			if (to_world.id != from_world.id):
				error = "Invalid operation. Cannot proceed to transfer"

			# Check currency.
			# Make sure the transfer is done from the correct currency.
			# If no movement, then it is irrealistic.
			if account_info['acc_type'] == Account.Type.deposit:
				if no_movements:
					currency_id = 1
				elif single_currency:
					currency_id = account_info['last_movement'][0]['currency']['id']
				else:
					select = request.form.get('currency_select')
					if select is None:
						error = "Please select in which currency you want the transfer"
					else:
						currency_id = int(select)

			# Check currency assuming a central account.
			# Make sure transfer is done from correcy currency.
			elif account_info['acc_type'] == Account.Type.central:
				if single_currency:
					currency_id = currencies[0]
				else:
					select = request.form.get('currency_select')
					if select is None:
						error = "Please select in which currency you want the transfer"
					else:
						currency_id = int(select)


			# Get balance of the account, and check if there are funds available.
			if account_info['acc_type'] == Account.Type.deposit:
				if no_movements:
						error = "Insuficient funds available to process the transfer"
				elif single_currency:
					exponent = account_info['last_movement'][0]['currency']['exponent']
					balance = account_info['last_movement'][0]['balance']
					integer_amount = round(amount * (10 ** exponent))
					if balance < integer_amount  or  balance <= 0:
						error = "Insuficient funds available to process the transfer"
				else:
					check_complete = False
					for last in account_info['last_movement']:
						if last['currency']['id'] == currency_id:
							balance = last['balance']
							exponent = last['currency']['exponent']
							integer_amount = round(amount * (10 ** exponent))
							if balance < integer_amount  or  balance <= 0:
								error = "Insuficient funds available to process the transfer"

							check_complete = True
							break

					if check_complete == False:
						error = "Something wrong happened when processing the currency"
						
						

		# Peform the actual transfer if no errors are there.
		if error is None:
			transfer_operation(
				currency_id=currency_id,
				from_account=acc_number,
				to_account=to_account.acc_number,
				value=amount,
				short_explanation=desc,
				long_explanation="",
			)
		
			# Redirect.
			return redirect(url_for('account.view', acc_number=acc_number))

		flash(error)


		

	# Send information.
	return render_template('account/transfer.html',
		acc_type=acc_type,
		acc_type_cap=acc_type.capitalize(),
		acc_number=acc_number,
		single_currency=single_currency,
		currencies=currencies,
		error=error
	)

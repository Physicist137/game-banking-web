import datetime
from .database import database_session
from .models import User, Account, Currency, World, Movement, CurrencyWorld
from .money import Money
from sqlalchemy import or_


# Set color function.
def color_function(value):
	if value < 0: return 'red'
	elif value == 0: return 'black'
	else: return 'blue'


# Write an HTML balance.
def html_balance(balance, text_balance):
	result = ""
	result += "<b><font color=\""
	result += color_function(balance)
	result += "\">" + str(text_balance)
	result += "</font></b>"
	return result


# Get balance of a given account.
def get_account_info(account_number):
	data = database_session.query(Account).filter(Account.acc_number == account_number).first()

	account = dict()
	account['id'] = data.id
	account['number'] = data.acc_number
	account['acc_type'] = data.acc_type

	# Fill up the world.
	account['world'] = dict()
	account['world']['id'] = data.world_id
	account['world']['name'] = database_session.query(World.name).filter(World.id == data.world_id).first()[0]

	# Get currencies list.
	data_currencies_world = database_session.query(CurrencyWorld) \
		.filter(CurrencyWorld.world_id == data.world_id).all()

	account['last_movement'] = []
	for data_currency_world in data_currencies_world:
		# Get the currency from the database.
		currency = database_session.query(Currency) \
			.filter(Currency.id == data_currency_world.currency_id).first()

		# Get the last movement in that currency.
		data_movement = database_session.query(Movement) \
			.filter(Movement.account_id == data.id) \
			.filter(Movement.currency_id == currency.id) \
			.order_by(Movement.processed_time.desc()).first()

		# Continue if there are no movements in the respective currency.
		if data_movement is None: continue

		# Build the last movement.
		last_movement = dict()
		last_movement['value'] = data_movement.value
		last_movement['balance'] = data_movement.balance
		last_movement['processed_time'] = data_movement.processed_time
		last_movement['currency'] = dict()
		last_movement['currency']['id'] = currency.id
		last_movement['currency']['iso'] = currency.iso
		last_movement['currency']['prefix'] = currency.prefix
		last_movement['currency']['posfix'] = currency.posfix
		last_movement['currency']['exponent'] = currency.exponent
		last_movement['currency']['name'] = currency.names

		# Append everything.
		account['last_movement'].append(last_movement)


	# Return the account balance.
	return account


def get_several_accounts_info(accounts_number):
	if len(accounts_number) == 0:  has_accounts = False
	else: has_accounts = True

	if has_accounts == False:
		return []

	# Get balance of each account.
	accounts_info = []
	for acc_number in accounts_number:
		info = get_account_info(acc_number)
		accounts_info.append(info)


	# Verify if there exists an account with multiple currencies.
	multiple_currencies_accounts = []
	has_account_multiple_currency = False
	for info in accounts_info:
		if len(info['last_movement']) > 1:
			multiple_currencies_accounts.append(info['number'])
			has_account_multiple_currency = True


	# If all accounts has a single currency, then:
	has_same_currency = False
	if not has_account_multiple_currency:
		# Verify if all accounts have the same currency.
		has_same_currency = True
		currencies_id = []

		for info in accounts_info:
			if len(info['last_movement']) != 0:
				currency_id = info['last_movement'][0]['currency']['id']
				if currency_id not in currencies_id:
					currencies_id.append(currency_id)

		if len(currencies_id) <= 1: has_same_currency = True
		else: has_same_currency = False

		if len(currencies_id) == 0: no_operations = True
		else: no_operations = False


	# Begin writing the accounts.
	accounts = []

	# If every single one has the same currency	
	if has_accounts:
		if has_same_currency == True:
			# Get currency data
			# Populate account array
			for info in accounts_info:
				account = dict()
				account['number'] = info['number']
				account['world'] = info['world']['name']
				account['world_id'] = info['world']['id']

				if len(accounts_info[0]['last_movement']) != 0:
					iso = accounts_info[0]['last_movement'][0]['currency']['iso']
					prefix = accounts_info[0]['last_movement'][0]['currency']['prefix']
					posfix = accounts_info[0]['last_movement'][0]['currency']['posfix']
					exponent = accounts_info[0]['last_movement'][0]['currency']['exponent']

					def from_value_to_html(balance):
						if prefix != "":
							text_balance = Money(balance, exponent).string(prefix=prefix+' ')
						elif posfix != "":
							text_balance = Money(balance, exponent).string(suffix=' '+posfix)
						else:
							text_balance = Money(balance, exponent).string(prefix=iso+' ')

						return html_balance(balance, text_balance) 
					
					if len(info['last_movement']) != 0:
						account['balance'] = from_value_to_html(info['last_movement'][0]['balance'])
						account['value'] = from_value_to_html(info['last_movement'][0]['value'])
						account['last_transaction'] = datetime.datetime \
							.fromtimestamp(info['last_movement'][0]['processed_time']) \
							.isoformat()

					else:
						account['balance'] = ""
						account['last_transaction'] = "No transaction was processed yet."

					
					
				accounts.append(account)


		# If they have different currencies, but no multiple currencies in a single account.
		elif not has_account_multiple_currency:
			for info in accounts_info:
				account = dict()
				account['number'] = info['number']
				account['world'] = info['world']['name']
				account['world_id'] = info['world']['id']
				if len(info['last_movement']) != 0:
					iso = info['last_movement'][0]['currency']['iso']
					exponent = info['last_movement'][0]['currency']['exponent']

					balance = info['last_movement'][0]['balance']
					text_balance = Money(balance, exponent).string(prefix=iso+' ')
					account['balance'] = html_balance(balance, text_balance)
					account['last_transaction'] = datetime.datetime \
						.fromtimestamp(info['last_movement'][0]['processed_time']) \
						.isoformat()
	
				else:
					account['balance'] = ""
					account['last_transaction'] = "No transaction was processed yet."

				accounts.append(account)


		# A single account has multiple currencies in it
		else:	
			for info in accounts_info:
				account = dict()
				account['number'] = info['number']
				account['world'] = info['world']['name']
				account['world_id'] = info['world']['id']
				balance_html_array = []
				last_transaction_array = []
				for balance in info['last_movement']:
					iso = balance['currency']['iso']
					exponent = balance['currency']['exponent']
					balance = balance['balance']
					text_balance = Money(balance, exponent).string(prefix=iso + ' ')
					balance_html_array.append(html_balance(balance, text_balance))

					# THIS IS WRONG. PLEASE FIX.
					last_transaction_array.append(info['last_movement'][0]['processed_time'])

				if len(balance_html_array) != 0:
					account['balance'] = ", ".join(balance_html_array)
					account['last_transaction'] = datetime.datetime \
						.fromtimestamp(max(last_transaction_array)) \
						.isoformat()
				else:
					account['balance'] = ""
					account['last_transaction'] = "No transaction was processed yet."

				accounts.append(account)

	# Return the expected result
	return accounts


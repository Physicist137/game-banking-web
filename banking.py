import datetime
from .database import database_session
from .models import Account, Transfer, Currency, Movement
from .money import Money


# Args: requested_account, from_account, to_account, value, short_explanation, long_explanation.
def add_money(**args):
	pass

# banking.banking.transfer_operation(currency_id=6, from_account=500, to_account=502, value=-1000.00, short_explanation='Transfer', long_explanation='Transfer', processed_time=datetime.datetime(2020, 7, 9, 14, 37).timestamp())


# No checking is made whatsoever. The transfer is done regardless of what.
# Args: currency_id, from_account, to_account, value, short_explanation, long_explanation.
# Opt Args: requested_account, processed_time
# XX: There's something wrong when it is asked to make transfers with equal processed_time.
def transfer_operation(**args):
	# Get the currency.
	exponent = database_session.query(Currency.exponent).filter(Currency.id == args['currency_id']).first()[0]
	integer_value = round(float(args['value'] * (10 ** exponent)))

	# Get proper account IDs.
	from_acc_id = database_session.query(Account.id).filter(Account.acc_number == args['from_account']).first()[0]
	to_acc_id = database_session.query(Account.id).filter(Account.acc_number == args['to_account']).first()[0]

	# Get processing time.
	if 'processed_time' in args: processed_time = args['processed_time']
	else: processed_time=round(datetime.datetime.utcnow().timestamp())

	# Get the requested account.
	if 'requested_account' in args:
		requested_account = args['requested_account']
	else:
		requested_account = args['from_account']

	# Set up the transfer.
	transfer = Transfer(
		currency_id=args['currency_id'],
		requested_account=requested_account,	
		from_account=from_acc_id,
		to_account=to_acc_id,
		processed_time=processed_time,
		value=integer_value,
		short_explanation=args['short_explanation'],
		long_explanation=args['long_explanation']
	)
	
	# Add in the database, and flushs it to get an id.
	database_session.add(transfer)
	database_session.flush()

	# Set up movement from the initial account.
	from_movement_data = database_session.query(Movement) \
		.filter(Movement.account_id == from_acc_id) \
		.filter(Movement.currency_id == args['currency_id']) \
		.order_by(Movement.processed_time.desc())	\
		.first()

	to_movement_data = database_session.query(Movement) \
		.filter(Movement.account_id == to_acc_id) \
		.filter(Movement.currency_id == args['currency_id']) \
		.order_by(Movement.processed_time.desc())	\
		.first()


	# Get previous balance.
	if from_movement_data == None:
		from_balance = 0
		from_last_movement_id = 0
	else: 
		from_balance = from_movement_data.balance
		from_last_movement_id = from_movement_data.id

	# Get previous balance.
	if to_movement_data == None:
		to_balance = 0
		to_last_movement_id = 0
	else:
		to_balance = to_movement_data.balance
		to_last_movement_id = to_movement_data.id

	# Set an explanation, if there's none.
	if args['short_explanation'] is None  or  args['short_explanation'] == "":
		from_short_description = "Transfer to account " + str(args['to_account'])
		to_short_description = "Transfer from account " + str(args['from_account'])
	else:
		from_short_description = args['short_explanation']
		to_short_description = args['short_explanation']


	# Set up from-movement.
	# Value is taken out from balance.
	from_movement = Movement(
		account_id = from_acc_id,
		currency_id = args['currency_id'],
		transfer_id=transfer.id,
		last_movement_id = from_last_movement_id,
		processed_time = processed_time,
		short_description=from_short_description,
		value = -integer_value,
		balance = from_balance - integer_value
	)

	# Set up to-movement
	# Value is added to balance.
	to_movement = Movement(
		account_id = to_acc_id,
		currency_id = args['currency_id'],
		transfer_id=transfer.id,
		last_movement_id = to_last_movement_id,
		processed_time = processed_time,
		short_description=to_short_description,
		value = +integer_value,
		balance = to_balance + integer_value
	)

	# Add movements into the database session and flush.
	database_session.add(from_movement)
	database_session.add(to_movement)
	database_session.flush()

	# Commit all changes to the database and finish.
	database_session.commit()



# Gets the balance of the account. A list in all currencies.
def get_balance(acc_number):
	pass

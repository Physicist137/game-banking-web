import datetime
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('currency', __name__, url_prefix='/currency')

from .auth import login_required
from .database import database_session
from .models import Currency


@bp.route('/list', methods=('GET', 'POST'))
def list():
	data_currencies = database_session.query(Currency).order_by(Currency.id).all()

	currencies = []
	for data in data_currencies:
		currency = dict()
		currency['id'] = data.id
		currency['iso'] = data.iso
		currency['where'] = data.from_where
		currency['names'] = data.names
		currencies.append(currency)

	return render_template('currency/list.html', currencies=currencies)

@bp.route('/view/<int:currency_id>', methods=('GET', 'POST'))
def view(currency_id):
	data_currency = database_session.query(Currency).filter(Currency.id == currency_id).first()

	currency = dict()
	currency['id'] = currency_id
	currency['iso'] = data_currency.iso
	currency['prefix'] = data_currency.prefix
	currency['posfix'] = data_currency.posfix
	currency['names'] = data_currency.names
	currency['exponent'] = data_currency.exponent
	currency['from_where'] = data_currency.from_where
	currency['short_description'] = data_currency.short_description
	currency['long_description'] = data_currency.long_description
	currency['reference'] = data_currency.reference

	return render_template('currency/view.html', currency=currency)


@login_required
@bp.route('/create', methods=('GET', 'POST'))
def create():
	if request.method == 'POST':
		user_id = session['user_id']
		error = None

		# Process worldname.
		names = request.form['names']
		if names == "" or names == None:
			error = "Name of the currency is lacking!"

		# Process ISO code.
		iso = request.form['iso']
		if iso == "" or iso == None:	
			error = "Currency ISO-4217 code is lacking"

		# process posfix and prefix.
		prefix = request.form['prefix']
		posfix = request.form['prefix']

		# Process decimal division
		mm = request.form['exponent']
		try: exponent = int(mm)
		except: error = "Invalid number of decimals! Fix it!"

		if exponent < 0:
			error = "Number of decimals can't be negative!"

		# process ISO code.
		from_where = request.form['from_where']
		short_description = request.form['short_description']
		long_description = request.form['long_description']
		reference = request.form['reference']


		# Finally save in the database.
		if error is None:
			currency = Currency(
				proposed_by=user_id,
				iso=iso,
				prefix=prefix,
				posfix=posfix,
				names=names,
				exponent=exponent,
				from_where=from_where,
				short_description=short_description,
				long_description=long_description,
				reference=reference,
				creation_date=round(datetime.datetime.utcnow().timestamp()),
				last_modification_date=round(datetime.datetime.utcnow().timestamp()),
				status=Currency.Status.pending
			)

			database_session.add(currency)
			database_session.commit()
			return redirect(url_for('currency.list'))


		# There were an error. Flash it.
		flash(error)

	
	# Didn't receive post request. Render page.
	return render_template('currency/create.html')

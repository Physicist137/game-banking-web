import click
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash

#engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
engine = create_engine('sqlite:///production_database.db', echo=False)
database_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
	from . import models
	models.Base.metadata.create_all(bind=engine)


def populate_db():
	from .models import Currency
	import datetime

	# Create US Dollar (USD).
	database_session.add(Currency(
		proposed_by = 0,
		iso='USD',
		prefix='$',
		posfix='dollars',
		names='United States Dollar, US Dollar',
		exponent=2,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/United_States_dollar',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Create Japanese Yen
	database_session.add(Currency(
		proposed_by = 0,
		iso='JPY',
		prefix='¥',
		posfix='yens',
		names='Japanese yen',
		exponent=0,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/Japanese_yen',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Create Euro.
	database_session.add(Currency(
		proposed_by = 0,
		iso='EUR',
		prefix='€',
		posfix='euros',
		names='Euro',
		exponent=2,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/Euro',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Create British Pound.
	database_session.add(Currency(
		proposed_by = 0,
		iso='GBP',
		prefix='£',
		posfix='ponds',
		names='Pound sterling',
		exponent=2,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/Pound_sterling',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Create Chinese Renminbi
	database_session.add(Currency(
		proposed_by = 0,
		iso='CNY',
		prefix='¥',
		posfix='yuans',
		names='Chinese yuan, Renminbi',
		exponent=2,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/Renminbi',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Create Brazilian Real.
	database_session.add(Currency(
		proposed_by = 0,
		iso='BRL',
		prefix='R$',
		posfix='reals',
		names='Brazilian real',
		exponent=2,
		from_where='Real World',
		short_description='',
		long_description='',
		reference='https://en.wikipedia.org/wiki/Brazilian_real',
		creation_date=round(datetime.datetime.utcnow().timestamp()),
		last_modification_date=round(datetime.datetime.utcnow().timestamp()),
		status=Currency.Status.accepted
	))

	# Commit changes.
	database_session.flush()
	database_session.commit()



@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('populate-db')
def populate_db_command():
    populate_db()
    click.echo('Standard values inserted.')

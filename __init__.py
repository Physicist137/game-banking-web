import os
from flask import Flask
from .database import database_session, init_db_command, populate_db_command

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		# SECRET_KEY='dev'
		SECRET_KEY=b"\xe5\xff'I\xcb\xa5\x0b\x02+\xb5\x1c\x07K\xaa@G"
	)

	# Initialize command database.
	app.cli.add_command(init_db_command)
	app.cli.add_command(populate_db_command)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
			pass

	from . import auth
	app.register_blueprint(auth.bp)

	from . import user
	app.register_blueprint(user.bp)

	from . import currency
	app.register_blueprint(currency.bp)

	from . import world
	app.register_blueprint(world.bp)

	from . import account
	app.register_blueprint(account.bp)

	from . import link
	app.register_blueprint(link.bp)

	@app.route('/hello')
	def hello():
		return "Hello world!"

	@app.teardown_appcontext
	def shutdown_session(exception=None):
		database_session.remove()


	return app



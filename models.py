from sqlalchemy import Column, Integer, String, Boolean, Binary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Currency(Base):
	__tablename__ = 'currency'

	id = Column(Integer, primary_key=True)
	proposed_by = Column(Integer, ForeignKey('user.id'), nullable=False)
	iso = Column(String(5), nullable=False, unique=True)
	prefix = Column(String(10), nullable=False)
	posfix = Column(String(10), nullable=False)
	names = Column(String, nullable=False)
	exponent = Column(Integer, nullable=False)
	
	# From where the currency is from: Ikariam, Star Wars, etc.
	from_where = Column(String(20))
	short_description = Column(String(100))
	long_description = Column(String)
	reference = Column(String(200))

	# Creation date.
	creation_date = Column(Integer, nullable=False)
	last_modification_date = Column(Integer, nullable=False)

	# Accepted or not.
	status = Column(Integer, nullable=False)

	class Status:
		accepted = 0
		pending = 1

	def __repr__(self):
		return "<Currency(three_leter='%s', symbol_prefix='%s', name_list='%s', dec_division=%d)>" % (
			self.id, self.three_leter, self.symbol_prefix,
			self.name_list, self.dec_division
		)


class User(Base):
	__tablename__ = 'user'
	
	id = Column(Integer, primary_key=True)
	username = Column(String(50), nullable=False)
	password = Column(String, nullable=False)
	email = Column(String(100))
	discord = Column(String(100))
	other = Column(String)

	email_validated = Column(Boolean, nullable=False)
	discord_validated = Column(Boolean, nullable=False)
	deleted = Column(Boolean, nullable=False)

	creation_time = Column(Integer, nullable=False)
	time_zone = Column(Integer, nullable=False)

	def __repr__(self):
		return "<User(nickname='%s')>" & (self.nickname,)


class World(Base):
	__tablename__ = 'world'

	id = Column(Integer, primary_key=True)
	owner_id = Column(Integer, ForeignKey('user.id'))
	deleted = Column(Boolean, nullable=False)
	creation_time = Column(Integer, nullable=False)

	# If the world is public or private.
	private = Column(Boolean, nullable=False)

	# Properties of the world
	max_account_per_user = Column(Integer, nullable=False)

	# Description data.
	name = Column(String(50), nullable=False)
	short_description = Column(String(100))
	long_description = Column(String)

	# Relationship.
	# owner = relationship("User", back_populates="worlds")

	def __repr__(self):
		return "<World(name='%s', owner='%s')>" % (
			self.name, self.owner
		)

#User.worlds = relationship("World", order_by=World.id, back_populates="owner")

class CurrencyWorld(Base):
	__tablename__ = 'currency_world'

	id = Column(Integer, primary_key=True)
	world_id = Column(Integer, ForeignKey('world.id'), nullable=False)
	currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
	creation_time = Column(Integer, nullable=False)



class Account(Base):
	__tablename__ = 'account'

	id = Column(Integer, primary_key=True)
	world_id = Column(Integer, ForeignKey('world.id'), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
	acc_number = Column(Integer, nullable=False, unique=True)
	acc_type = Column(Integer, nullable=False)
	deleted = Column(Boolean, nullable=False)
	creation_time = Column(Integer, nullable=False)
	
	short_description = Column(String(100))
	long_description = Column(String)

	#world = relationship("World", back_populates="accounts")
	#user = relationship("User", back_populates="accounts")

	class Type:
		deposit = 0
		central = 1

	# TOBE IMPLEMENTED.
	#class Status:
	#	active = 0
	#	frozen = 1
	#	suspended = 2

	def __repr__(self):
		return "<Account(acc_number='%s', acc_type='%d')>" % (
			self.acc_number, self.acc_type
		)

#World.accounts = relationship("Account", order_by=Account.id, back_populates="world");
#User.accounts = relationship("Account", order_by=Account.id, back_populates="user");


class Transfer(Base):
	__tablename__ = 'transfer'
	
	id = Column(Integer, primary_key=True)

	# Transfer is done in which currency.
	currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)

	# Who requested the transaction.
	# From whom the value will be taken, to whom will be sent.
	requested_account = Column(Integer, ForeignKey('account.id'), nullable=False)
	from_account = Column(Integer, ForeignKey('account.id'), nullable=False)
	to_account = Column(Integer, ForeignKey('account.id'), nullable=False)

	# Requested time: Which time transaction was requested.
	processed_time = Column(Integer, nullable=False)

	# The value of the transaction.
	value = Column(Integer, nullable=False)

	# Description.
	short_explanation = Column(String(100))
	long_explanation = Column(String)

	def __repr__(self):
		return "<Transaction(value=%d)>" % (
			self.value
		)


# Implement Orders class.
# Scheduling one-time transfer orders.
# Scheduling periodic transfer orders.


class Movement(Base):
	__tablename__ = 'movement'

	id = Column(Integer, primary_key=True)
	account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
	currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
	transfer_id = Column(Integer, ForeignKey('transfer.id'), nullable=False)
	last_movement_id = Column(Integer, ForeignKey('movement.id'), nullable=False)
	
	processed_time = Column(Integer, nullable=False)
	value = Column(Integer, nullable=False)
	balance = Column(Integer, nullable=False)
	short_description = Column(String(100))



class Link(Base):
	__tablename__ = 'link'
	
	id = Column(Integer, primary_key=True)
	world_id = Column(Integer, ForeignKey('world.id'), nullable=False)
	creation_date = Column(Integer, nullable=False)
	expire_date = Column(Integer, nullable=False)
	status = Column(Integer, nullable=False)
	link = Column(String(128), nullable=False)

	class Status:
		active = 0
		disabled = 1


# Help/Ticket support.
class HelpSupport(Base):
	__tablename__ = 'help'

	# ID of the reply.	
	id = Column(Integer, primary_key=True)
	email = Column(String(50))
	time = Column(Integer, nullable=False)
	passphrase = Column(String(50), nullable=False)
	status = Column(Integer, nullable=False)


class Ticket(Base):
	__tablename__ = 'ticket'

	# ID of the reply.	
	id = Column(Integer, primary_key=True)
	help_id = Column(Integer, ForeignKey('help.id'), nullable=False)
	time = Column(Integer, nullable=False)
	content = Column(String, nullable=False)


class BinaryStorage(Base):
	__tablename__ = 'binary_storage'
	
	id = Column(Integer, primary_key=True)
	help_id = Column(Integer, ForeignKey('help.id'), nullable=False)
	ticket_id = Column(Integer, ForeignKey('ticket.id'), nullable=False)
	time = Column(Integer, nullable=False)
	filename = Column(String(50), nullable=False)
	binary = Column(Binary, nullable=False)

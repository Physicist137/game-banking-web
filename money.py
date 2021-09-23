

class Money:
	def __init__(self, integer=0, decimal=2):
		self.integer = integer
		self.decimal = decimal

	def float_value(self):
		return round(self.integer / (10 ** self.decimal), self.decimal)

	def cent(self):
		return abs(self.integer) % (10 ** self.decimal)

	def real(self):
		return abs(self.integer) // (10 ** self.decimal)

	def cent_string(self):
		abs_cent_str = str(self.cent())
		zero_number = self.decimal - len(str(self.cent()))
		zeros = '0' * zero_number
		return zeros + abs_cent_str

	def real_string(self, separator=""):
		abs_real_str = str(self.real())

		result = ""
		if (separator != ""):
			comma_number = len(abs_real_str) // 3
			rest = len(abs_real_str) % 3
			result += abs_real_str[0:rest]

			init = 0
			if (rest == 0 and comma_number != 0):
				result += abs_real_str[rest : 3 + rest]
				init = 1

			for i in range(init, comma_number):
				result += separator + abs_real_str[3*i + rest : 3*(i+1) + rest]
		else:
			result = abs_real_str

		if (self.integer < 0):
			return '-' + result
		else:
			return '+' + result
			
	# Parameters:
	# prefix, suffix.
	# thousand_separator, decimal_separator
	def string(self, **parameter):
		result = ""
		
		# Add prefix.
		if ('prefix' in parameter):
			result += parameter['prefix']
		else:
			result += "R$ "

		# Add the real value
		if ('thousand_separator' in parameter):
			result += self.real_string(parameter['thousand_separator'])
		else:
			result += self.real_string(',')

		# Add the decimal part
		if ('decimal_separator' in parameter):
			result += parameter['decimal_separator']
		else:
			result += "."

		# Add the cents
		result += self.cent_string()	

		# Add suffix
		if ('suffix' in parameter):
			result += parameter['suffix']

		return result

	# Display the money on screen.
	def __repr__(self):
		return self.string()

	# Adding two amounts of money.
	def __add__(self, other):
		return Money(self.integer + other.integer, self.decimal)

	# Subtracting two amounts of money.
	def __sub__(self, other):
		return Money(self.integer - other.integer, self.decimal)

	# Multiplying amount of money by an integer.
	def __mul__(self, other):
		if (isinstance(other, int) == False):
			raise ValueError("Number is not integer. Cannot multiply.")

		return Money(self.integer * other, self.decimal)

	# Negating the money.
	def __neg__(self):
		return Money(-self.integer, self.decimal)

	# Positivating the money.
	def __pos__(self):
		return Money(+self.integer, self.decimal)

	# Absolute value
	def __abs__(self):
		return Money(abs(self.integer), self.decimal)



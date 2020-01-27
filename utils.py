def overload(value, string, integer):
	if type(value) == str:
		return string
	elif type(value) == int:
		return integer
	else:
		raise Exception("!")

def callOverload(value, string, integer):
	overload(value, string, integer)(value)
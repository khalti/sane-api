class SaneException(Exception):
	pass

class UnmetDependency(SaneException):
	def __init__(self, path):
		msg = "The request payload has unmet dependency, '{}'."
		self.message = msg.format(".".join(path))

class CyclicDependency(SaneException):
	def __init__(self, key):
		self.message = "The request payload has cyclic dependency at '{}'.".format(key)

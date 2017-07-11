class SaneException(Exception):
	pass

class UnmetDependency(SaneException):
	pass

class CyclicDependency(SaneException):
	def __init__(self, key):
		self.message = "The request payload has cyclic dependency at '{}'.".format(key)

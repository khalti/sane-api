import re
import json


def has_cyclic_dependency(data, entry_key, this_key):
	if entry_key == this_key:
		return True

	value = data[this_key or entry_key]
	matches = re.findall(r"{([a-zA-Z0-9_.]+?)}", json.dumps(value))
	for match in matches:
		next_key = match.split(".")[0]
		if has_cyclic_dependency(data, entry_key, next_key):
			return True
	return False

def get_cyclic_dependency(data):
	"""
	Returns root key which has cyclic dependency.
	"""
	for key, value in data.items():
		if has_cyclic_dependency(data, key, this_key=None):
			return key
	return None

def get_unmet_dependency(data):
	"""
	Returns root key which has unmet dependency.
	"""
	for key, value in data.items():
		matches = re.findall(r"{([a-zA-Z0-9_.]+?)}", json.dumps(value))
		for match in matches:
			try:
				dependency = match.split(".")[0]
				data[dependency]
			except KeyError:
				return [key, dependency]
	return None

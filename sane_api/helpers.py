import re
import json
import copy
from functools import reduce

from sane_api.exceptions import UnmetDependency


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

def get_value_at(path, source, start=False, walked=[]):
	if type(source) is list:
		dlist = map\
				(lambda x: get_value_at\
					(copy.deepcopy(path), x, start, walked), source)
		return reduce(lambda x, y: "{},{}".format(x,y), dlist)

	if len(path) == 0:
		return source

	this_path = path.pop(0)
	walked.append(this_path)

	try:
		return get_value_at\
				(path, source[this_path], walked=walked)
	except KeyError as e:
		if not start:
			raise UnmetDependency(walked)
		raise e

def fill_template(req_sig, responses):
	"""
	Fills the template and returns filled request signature else
	returns None if template is not fillable due to dependencies.
	"""
	req_sig_str = json.dumps(req_sig)
	matches = re.findall(r"{([a-zA-Z0-9\.]+)}", req_sig_str)
	for match in matches:
		path = match.split(".")
		pattern = "{" + match + "}"
		try:
			value = get_value_at\
					(copy.deepcopy(path), responses, start=True, walked=[])
			req_sig = json.loads\
					(json.dumps(req_sig).replace(pattern, str(value)))
		except KeyError:
			return None

	return req_sig

def make_requests(client, req_sigs, response={}, pendings=[]):
	if len(req_sigs) == 0:
		return responses

	key, req_sig = req_sigs.pop(0)
	processed_sig = fill_template(req_sig, responses)
	if not processed_sig:
		pendings.append(key)
		req_sigs.append([key, req_sig])
	else:
		s = CompositeRequestSerializer(data = processed_sig)
		if not s.is_valid():
			responses[key] = s.errors

		response = self.client.get \
				( s.validated_data["url"]
				, s.validated_data.get("query", {})
				, format="json"
				)

		responses[key] = response.json() if response.status_code == 200 else None

	return make_requests(requests, responses, pendings)

def make_nested_requests():
	pass

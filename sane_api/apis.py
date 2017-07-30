import copy
import re
from functools import reduce
import ast
import json

from rest_framework.viewsets import (ModelViewSet, ViewSet, )
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.test import APIClient

from sane_api.serializers import CompositeRequestSerializer
from sane_api.exceptions import SaneException, CyclicDependency, UnmetDependency


class SanePermissionClass:
	def _get_action_name(self, view, request):
		return view.action or request.method.lower()

	def _get_authorizer(self, request, view, obj = None):
		instance = obj or view
		action_name = self._get_action_name(view, request)

		try:
			return getattr(instance, "can_{}".format(action_name))
		except AttributeError as e:
			return None

	def has_permission(self, request, view):
		authorizer = self._get_authorizer(request, view)
		return authorizer and not not authorizer(request.user, request)

	def has_object_permission(self, request, view, obj):
		authorizer = self._get_authorizer(request, view, obj)
		return authorizer and not not authorizer(request.user, request)

class SaneAPIMixin:
	permission_classes = [SanePermissionClass]

class SaneModelAPI(SaneAPIMixin, ModelViewSet):
	def get_queryset(self):
		raise Exception("Please implement .get_queryset() and tailor it for specific user/group.")

class SaneAPI(SaneAPIMixin, ViewSet):
	pass


class HelperAPI(SaneAPI):
	def get_value_at(self, to_walk, source, start=False, walked=[]):
		if type(source) is list:
			dlist = map\
					(lambda x: self.get_value_at\
						(copy.deepcopy(to_walk), x, start, walked), source)
			return reduce(lambda x, y: "{},{}".format(x,y), dlist)

		if len(to_walk) == 0:
			return source

		this_path = to_walk.pop(0)
		walked.append(this_path)
		if start and not self.request.data.get(this_path):
			raise UnmetDependency(walked)

		try:
			return self.get_value_at\
					(to_walk, source[this_path], walked=walked)
		except KeyError as e:
			if not start:
				raise UnmetDependency(walked)
			raise e

	def fill_template(self, req_sig, responses):
		req_sig_str = json.dumps(req_sig)
		match = re.search(r"{([a-zA-Z0-9\.]+)}", req_sig_str)
		if match:
			for group in match.groups():
				path = group.split(".")
				pattern = "{" + group + "}"
				try:
					value = self.get_value_at\
							(copy.deepcopy(path), responses, start=True, walked=[])
					req_sig = json.loads(req_sig_str.replace(pattern, str(value)))
				except KeyError:
					return None

		return req_sig

	def get_sub_requests(self, requests, responses, pendings):
		if len(requests) == 0:
			return responses

		key, req_sig = requests.pop(0)
		processed_sig = self.fill_template(req_sig, responses)
		if not processed_sig:
			pendings.append(key)
			requests.append([key, req_sig])
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

		return self.get_sub_requests(requests, responses, pendings)

	def walk(self, key, requests, dependents):
		occurances = filter(lambda dependent: dependent == key, dependents)
		if len(list(occurances)) > 2:
			raise CyclicDependency(key)

		try:
			match = re.search(r"{([a-zA-Z0-9_.]+?)}", json.dumps(requests[key]))
		except KeyError:
			raise UnmetDependency([key])

		if not match:
			return
		dependents.append(key)
		for group in match.groups():
			self.walk(group.split(".")[0], requests, dependents)

	def check_cyclic_dependency(self, requests):
		for key, value in requests.items():
			self.walk(key, requests, dependents=[])

	@list_route(methods=["post"])
	def compose(self, request):
		try:
			self.check_cyclic_dependency(request.data)
		except SaneException as e:
			return Response({"detail": e.message}, status=400)

		self.client = APIClient()
		if request.user and request.user.is_authenticated():
			client.force_authenticate(request.user)

		requests = []
		for key, value in request.data.items():
			requests.append([key, value])

		try:
			responses = self.get_sub_requests(requests, responses={}, pendings=[])
		except SaneException as e:
			return Response({"detail": e.message}, status=400)
		return Response(responses, status=200)

	def can_compose(self, user, request):
		return True

	@list_route(methods=["get"])
	def doc(self, request):
		pass

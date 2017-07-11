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
from sane_api.exceptions import SaneException, CyclicDependency


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
	def get_value_at(self, path, source):
		if type(source) is list:
			dlist = map(lambda x: self.get_value_at(copy.deepcopy(path), x), source)
			return reduce(lambda x, y: "{},{}".format(x,y), dlist)

		if len(path) == 0:
			return source
		this_path = path.pop(0)
		return self.get_value_at(path, source[this_path])

	def fill_template(self, req_sig, responses):
		req_sig_str = json.dumps(req_sig)
		match = re.search(r"{([a-zA-Z0-9\.]+)}", req_sig_str)
		if match:
			for group in match.groups():
				path = group.split(".")
				pattern = "{" + group + "}"
				try:
					value = self.get_value_at(copy.deepcopy(path), responses)
					req_sig = json.loads(req_sig_str.replace(pattern, str(value)))
				except (KeyError, TypeError):
					return None

		return req_sig

	def get_sub_requests(self, requests, responses={}, pending=[]):
		if len(requests) == 0:
			return responses

		key, req_sig = requests.pop(0)
		processed_sig = self.fill_template(req_sig, responses=[])
		if not processed_sig:
			if key in pending:
				raise CyclicDependency(key)
			pending.append(key)
			requests.append([key, req_sig])
		else:
			s = CompositeRequestSerializer(data = processed_sig)
			if not s.is_valid():
				responses[key] = s.errors

			responses[key] = self.client.get \
					( s.validated_data["url"]
					, s.validated_data.get("query", {})
					, format="json"
					).json()

		return self.get_sub_requests(requests, responses, pending)

	@list_route(methods=["post"])
	def compose(self, request):
		self.client = APIClient()
		if request.user and request.user.is_authenticated():
			client.force_authenticate(request.user)

		requests = []
		for key, value in request.data.items():
			requests.append([key, value])

		try:
			responses = self.get_sub_requests(requests)
		except SaneException as e:
			return Response({"detail": e.message}, status=400)
		return Response(responses, status=200)

	def can_compose(self, user, request):
		return True

	@list_route(methods=["get"])
	def doc(self, request):
		pass

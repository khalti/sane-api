from rest_framework.viewsets import (ModelViewSet, ViewSet, )
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.test import APIClient


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
	@list_route(methods=["post"])
	def compose(self, request):
		client = APIClient()
		if request.user and request.user.is_authenticated():
			client.force_authenticate(request.user)

		print(request.data)
		return Response({"detail": "Yo"}, status=200)

	def can_compose(self, user, request):
		return True

	@list_route(methods=["get"])
	def doc(self, request):
		pass

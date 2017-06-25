import inspect

from rest_framework.viewsets import (ModelViewSet, ViewSet, )
from rest_framework.response import Response
from rest_framework import status


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

	def get_serializer_class(self):
		# resolve serializers based upon the versions of api
		pass

class SaneModelAPI(SaneAPIMixin, ModelViewSet):
	def filter_queryset(self, queryset):
		raise Exception("Please implement this method to filter queryset as per user/role.")

	def update(self, request, pk):
		return Response \
				( {"detail": "Action not implement."}
				, status = status.HTTP_501_NOT_IMPLEMENTED
				)


class SaneAPI(SaneAPIMixin, ViewSet):
	pass

import re
from functools import partial
import json

from django.db import models
from rest_framework.serializers import \
		( BaseSerializer
		, Serializer
		, ModelSerializer
		, ListSerializer
		, Field
		, CharField
		, JSONField
		)

class PermissionField(Field):
	def __init__(self, *args, **kwargs):
		kwargs["read_only"] = True
		super(PermissionField, self).__init__(*args, **kwargs)

	def to_representation(self, obj):
		request = self.context["request"]
		permission_methods = filter(lambda method: re.match("can_", method), dir(obj))
		permissions = []
		for permission_method in permission_methods:
			permission_name = permission_method.replace("can_", "")
			authorizer = getattr(obj, permission_method)
			if authorizer(request.user, request):
				permissions.append(permission_name)
		return permissions

	def get_attribute(self, instance):
		return instance

class SaneSerializerMixin:
	def __init__(self, *args, **kwargs):
		super(SaneSerializerMixin, self).__init__(*args, **kwargs)
		if not hasattr(self, "context") or not self.context.get("request"):
			return

		request = self.context.get("request")
		available_fields = set(self.fields.keys())
		accessible_fields = self.get_accessible_fields()
		requested_fields = self.get_requested_fields()

		field_groups = [available_fields, accessible_fields, requested_fields]
		self.final_fields = set.intersection(*field_groups)

		for field in available_fields - self.final_fields:
			self.fields.pop(field)

	def get_accessible_fields(self):
		request_method = self.context["request"].method.lower()
		if request_method == "get":
			return set(self.get_readable_fields())
		else:
			return set(self.get_writable_fields())

	def get_requested_fields(self):
		fields_str = self.context["request"].query_params.get("fields")
		accessible_fields = self.get_accessible_fields()
		if not fields_str:
			return accessible_fields
		return fields_str.split(",")

	def to_representation(self, obj):
		"""
		Assign 'None' to inaccessible or unavailable fields.
		Helps in backwark compatibility.
		"""
		data = super(SaneSerializerMixin, self).to_representation(obj)

		if not hasattr(self, "context") or not self.context.get("request"):
			return data

		empty_fields = set.difference(set(self.get_requested_fields()), set(data.keys()))
		for field in empty_fields:
			data[field] = None
		return data

	def get_readable_fields(self):
		raise Exception \
				("Please implement this method and so that it returns different fields for different user/group.")

	def get_writable_fields(self):
		raise Exception \
				("Please implement this method and so that it returns different fields for different user/group.")

class SaneSerializer(SaneSerializerMixin, Serializer):
	pass

class SaneModelSerializer(SaneSerializerMixin, ModelSerializer):
	permissions = PermissionField()

class CompositeRequestSerializer(Serializer):
	url = CharField()
	query = JSONField(required=False)

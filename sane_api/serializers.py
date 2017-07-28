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
		, ListSerializer
		)
from sane_api.exceptions import SaneException

class SaneListSerializer(ListSerializer):
	def __init__(self, *args, **kwargs):
		if not kwargs.get("max_length"):
			raise SaneException("Keyword arg 'max_length' is required for nested serializers with many=True.")
		self._max_length = kwargs.pop("max_length")
		super(SaneListSerializer, self).__init__(*args, **kwargs)

	def to_representation(self, data):
		"""
		List of object instances -> List of dicts of primitive datatypes.
		"""
		# Dealing with nested relationships, data can be a Manager,
		# so, first get a queryset from the Manager if needed
		iterable = data.all() if isinstance(data, models.Manager) else data

		return [
			self.child.to_representation(item) for item in iterable[:self._max_length]
		]

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
		if kwargs.get("max_length"):
			self._max_length = kwargs.pop("max_length")
		super(SaneSerializerMixin, self).__init__(*args, **kwargs)
		if not hasattr(self, "context") or not self.context.get("request"):
			return

		request = self.context.get("request")
		request_method = request.method.lower()
		available_fields = set(self.fields.keys())
		accessible_fields, requested_fields = None, None
		if request_method == "get":
			accessible_fields = set(self.get_readable_fields())
			fields_str = self.context.get("fields") or request.query_params.get("fields") or {}
			self._requested_fields = self.normalize_fields_str(fields_str)
			requested_fields = self._requested_fields.keys()
			self.reinitialize_fields()
		else:
			accessible_fields = set(self.get_writable_fields())

		field_groups = [available_fields, accessible_fields, requested_fields]
		valid_field_groups = filter(lambda group: not not group, field_groups)
		self.final_fields = set.intersection(*valid_field_groups)

		for field in available_fields - self.final_fields:
			self.fields.pop(field)

	def to_representation(self, obj):
		"""
		Assign 'None' to inaccessible or unavailable fields.
		Helps in backwark compatibility.
		"""
		data = super(SaneSerializerMixin, self).to_representation(obj)
		empty_fields = set.difference(set(self._requested_fields.keys()), set(data.keys()))
		for field in empty_fields:
			data[field] = None
		return data

	def normalize_fields_str(self, fields_str):
		if type(fields_str) is dict:
			return fields_str

		fields_str = re.sub(r"{", ":{", fields_str)
		fields_str = "{" + fields_str + "}"
		# fields_str = re.sub(r"}", "]}", fields_str)
		# fields_str = re.sub(r"([a-zA-Z0-9_]+?:\[)", "{\\1", fields_str)
		fields_str = re.sub(r"([a-zA-Z0-9_]+)", "\"\\1\"", fields_str)
		fields_str = re.sub(r'("[a-zA-Z0-9_]+")([,}])', "\\1:null\\2", fields_str)
		return json.loads(fields_str)

	def reinitialize_fields(self):
		for field, value in self.fields.items():
			if isinstance(value, BaseSerializer):
				self.reinitialize_nested_serializer(field, value)


	def reinitialize_nested_serializer(self, field, value):
		if isinstance(value, BaseSerializer):
			args = value._args
			kwargs = value._kwargs
			self.context["fields"] = self._requested_fields.get(field, {})
			kwargs["context"] = self.context
			if isinstance(value, ListSerializer):
				child = kwargs.pop("child")
				kwargs["max_length"] = child._max_length
				kwargs["child"] = type(child)(*args, **kwargs)
				self.fields[field] = SaneListSerializer(*args, **kwargs)
			else:
				self.fields[field] = type(value)(*args, **kwargs)

class SaneSerializer(SaneSerializerMixin, Serializer):
	pass

class SaneModelSerializer(SaneSerializerMixin, ModelSerializer):
	permissions = PermissionField()

class CompositeRequestSerializer(Serializer):
	url = CharField()
	query = JSONField(required=False)

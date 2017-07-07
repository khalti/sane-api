import re
from functools import partial

from rest_framework.serializers import \
		( BaseSerializer
		, Serializer
		, ModelSerializer
		, ListSerializer
		, Field
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

		if not self.context or not self.context.get("request"):
			return

		request = self.context.get("request")
		request_method = request.method.lower()
		available_fields = set(self.fields.keys())

		accessible_fields, requested_fields = None, None
		if request_method == "get":
			accessible_fields = set(self.get_readable_fields())
			requested_fields = self._get_requested_fields(self.context)
		else:
			accessible_fields = set(self.get_writable_fields())

		field_groups = [available_fields, accessible_fields, requested_fields]
		valid_field_groups = filter(lambda group: not not group, field_groups)
		final_fields = set.intersection(*valid_field_groups)

		for field in available_fields - final_fields:
			self.fields.pop(field)

	def _get_requested_fields(self, context):
		request = context["request"]
		fields = context.get("fields") or request.query_params.get("fields") or []
		
		if type(fields) is str:
			return set(fields.split(","))

		requested_fields = []
		for field in fields:
			if type(field) is dict:
				field_name = list(field)[0]
				nested_field = self.fields[field_name]
				if isinstance(nested_field, BaseSerializer):
					args = nested_field._args
					kwargs = nested_field._kwargs
					self.context["fields"] = field[field_name]
					kwargs["context"] = self.context
					if isinstance(nested_field, ListSerializer):
						original_serializer = kwargs.pop("child")
						kwargs["many"] = True
						self.fields[field_name] = type(original_serializer)(*args, **kwargs)
					else:
						self.fields[field_name] = type(nested_field)(*args, **kwargs)
				requested_fields.append(field_name)
			else:
				requested_fields.append(field)
		return requested_fields

class SaneSerializer(SaneSerializerMixin, Serializer):
	pass

class SaneModelSerializer(SaneSerializerMixin, ModelSerializer):
	permissions = PermissionField()

from rest_framework.serializers import Serializer, ModelSerializer

class SaneSerializerMixin:
	def __init__(self, *args, **kwargs):
		super(SaneSerializerMixin, self).__init__(*args, **kwargs)

		if not self.context or not self.context.get("request"):
			return

		request = self.context.get("request")
		request_method = request.method.lower()
		available_fields = set(self.fields.keys())

		if request_method == "get":
			accessible_fields = set(self.get_readable_fields())
		else:
			accessible_fields = set(self.get_writable_fields())

		if request_method == "get":
			requested_fields = set(request.query_params.get("fields") or [])
		elif request.method == "patch":
			requested_fields = set(kwargs["data"].keys())

		if request_method in ["post", "put"]:
			final_fields = accessible_fields
		else:
			final_fields = set.intersection(accessible_fields, requested_fields)

		for field in available_fields - final_fields:
			self.fields.pop(field)

class SaneSerializer(SaneSerializerMixin, Serializer):
	pass

class SaneModelSerializer(SaneSerializerMixin, ModelSerializer):
	pass

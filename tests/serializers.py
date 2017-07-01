from unittest.mock import patch

from django.test import TestCase
from django.db import models
from rest_framework.test import APIRequestFactory
from rest_framework import serializers

from sane_api.serializers import SaneSerializer, SaneModelSerializer

factory = APIRequestFactory()

class ASaneSerializer(SaneSerializer):
	field1 = serializers.IntegerField()
	field2 = serializers.IntegerField()
	field3 = serializers.IntegerField()
	field4 = serializers.IntegerField()
	field5 = serializers.IntegerField()

	def get_readable_fields(self):
		return ['field1', 'field2', 'field3']

	def get_writable_fields(self):
		return ['field2', 'field3', 'field4']

class AnObject:
	field1 = 1
	field2 = 2
	field3 = 3
	field4 = 4
	field5 = 5

class TestSaneSerializer(TestCase):
	def test1(self):
		fields = "field1,field2"
		request = factory.get("/", content_type='application/json')
		request.query_params = {"fields": fields}
		s = ASaneSerializer(AnObject, context = {"request": request})
		assert s.data == {"field1": 1, "field2": 2}, \
			"It returns requested readable fields."

	def test2(self):
		fields = "field4,field5"
		request = factory.get("/", content_type='application/json')
		request.query_params = {"fields": fields}
		s = ASaneSerializer(AnObject, context = {"request": request})
		assert s.data == {}, \
			"It returns empty dict if requested fields are not accessible."

	def test3(self):
		fields = "field6,field7"
		request = factory.get("/", content_type='application/json')
		request.query_params = {"fields": fields}
		s = ASaneSerializer(AnObject, context = {"request": request})
		assert s.data == {}, \
			"It returns empty dict if requested fields are not availabe."

	def test4(self):
		request = factory.post("/", content_type='application/json')
		data = \
			{ "field1": 1
			, "field2": 2
			, "field3": 3
			, "field4": 4
			}
		s = ASaneSerializer(data = data, context = {"request": request})
		s.is_valid()

		expected_data = \
				{ "field2": 2
				, "field3": 3
				, "field4": 4
				}
		assert s.validated_data == expected_data, \
			"It returns writable fields for post request."

	def test5(self):
		request = factory.post("/", content_type='application/json')
		data = \
			{ "field1": 1
			, "field2": 2
			, "field3": 3
			, "field4": 4
			}
		s = ASaneSerializer(AnObject, data = data, context = {"request": request})
		s.is_valid()

		expected_data = \
				{ "field2": 2
				, "field3": 3
				, "field4": 4
				}
		assert s.validated_data == expected_data, \
			"It returns writable fields for put request."

	def test6(self):
		request = factory.post("/", content_type='application/json')
		data = \
			{ "field3": 3
			, "field4": 4
			}
		s = ASaneSerializer(AnObject, data = data, context = {"request": request})
		s.is_valid()

		expected_data = \
				{ "field3": 3
				, "field4": 4
				}
		assert s.data == expected_data, \
			"It returns fields being patched for patch request."

	def test7(self):
		request = factory.get("/", content_type='application/json')
		request.query_params = {}
		s = ASaneSerializer(AnObject, context = {"request": request})
		expected = \
				{ "field1": 1
				, "field2": 2
				, "field3": 3
				}
		assert s.data == expected, \
			"It returns all the fields if 'fields' are not specified."

	def test8(self):
		class AModel(models.Model):
			field1 = models.IntegerField()

			class Meta:
				app_label="tests"

			def can_retrieve(self, user, request):
				return True

			def can_update(self, user, request):
				return False

			def can_destroy(self, user, request):
				return True

		class BSaneSerializer(SaneModelSerializer):
			field1 = serializers.IntegerField()

			def get_readable_fields(self):
				return ['field1', 'permissions']

			class Meta:
				model = AModel
				fields = "__all__"
				app_label = "bruno"

		request = factory.get("/", content_type='application/json')
		request.query_params = {}
		request.user = {}

		amodel = AModel(field1=1)
		s = BSaneSerializer(amodel, context = {"request": request})
		expected = \
				{ "field1": 1
				, "permissions": ["destroy", "retrieve"]
				}
		assert s.data == expected, "It includes 'permissions' field."

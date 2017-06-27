from unittest.mock import patch

from django.test import TestCase
from django.db import models

from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import detail_route, list_route

from sane_api.api import SaneAPIMixin, SaneAPI, SaneModelAPI

factory = APIRequestFactory()

class ASaneAPI(SaneAPI):
	@list_route(methods=["post"])
	def create(self, request):
		return Response \
			({"detail": "Created something."}, status = status.HTTP_201_CREATED)

	def can_create(self, user, request):
		return True

	@list_route(methods=["get"])
	def list(self, request):
		return Response \
			({"detail": "List stuff."}, status = status.HTTP_200_OK)

class TestSaneAPI(TestCase):
	def test1(self):
		request = factory.post('/', '', content_type='application/json')
		aview = ASaneAPI.as_view(actions= {'post': 'create', })
		response = aview(request)

		assert response.status_code == 201, \
			"It allows an action, if an action authorizer at api returns True."

	@patch.object(ASaneAPI, "can_create")
	def test2(self, mock):
		mock.return_value = False
		request = factory.post('/', '', content_type='application/json')
		aview = ASaneAPI.as_view(actions= {'post': 'create', })
		response = aview(request)

		assert response.status_code == 403, \
			"If disallows an action, if an action authorizer at api returns False."

	@patch.object(ASaneAPI, "can_create")
	def test3(self, mock):
		mock.return_value = None
		request = factory.post('/', '', content_type='application/json')
		aview = ASaneAPI.as_view(actions= {'post': 'create', })
		response = aview(request)

		assert response.status_code == 403, \
			"It disallows, if an action authorize at api returns nothing."

	def test4(self):
		request = factory.post('/', '', content_type='application/json')
		aview = ASaneAPI.as_view(actions= {'get': 'list', })
		response = aview(request)

		assert response.status_code == 403, \
			"It disallows, if an authorize at api is absent."

class AModel(models.Model):
	name = models.CharField(max_length=20)

	class Meta:
		app_label="tests"

	def can_destroy(self, user, request):
		return True

class ASaneModelAPI(SaneModelAPI):
	queryset = AModel.objects.all()

	def perform_destroy(self, obj):
		pass

	def can_destroy(self, user, request):
		return True

	def can_retrieve(self, user, request):
		return True

class TestSaneModelAPI(TestCase):
	@patch("rest_framework.generics.get_object_or_404")
	def test1(self, mock):
		mock.return_value = AModel()
		request = factory.delete('/', '', content_type='application/json')
		aview = ASaneModelAPI.as_view(actions= {'delete': 'destroy', })
		response = aview(request, pk=1)

		assert response.status_code == 204, \
			"It allows an action, if model authorizer returns True."

	@patch.object(AModel, "can_destroy")
	@patch("rest_framework.generics.get_object_or_404")
	def test2(self, mock1, mock2):
		mock1.return_value = AModel()
		mock2.return_value = False
		request = factory.delete('/', '', content_type='application/json')
		aview = ASaneModelAPI.as_view(actions= {'delete': 'destroy', })
		response = aview(request, pk=1)

		assert response.status_code == 403, \
			"It disallows, if action authorizer at model returns False."

	@patch.object(AModel, "can_destroy")
	@patch("rest_framework.generics.get_object_or_404")
	def test3(self, mock1, mock2):
		mock1.return_value = AModel()
		mock2.return_value = None
		request = factory.delete('/', '', content_type='application/json')
		aview = ASaneModelAPI.as_view(actions= {'delete': 'destroy', })
		response = aview(request, pk=1)

		assert response.status_code == 403, \
			"It disallows, if action authorizer at model returns nothing."

	@patch("rest_framework.generics.get_object_or_404")
	def test4(self, mock):
		mock.return_value = AModel
		request = factory.get('/', '', content_type='application/json')
		aview = ASaneModelAPI.as_view(actions= {'get': 'retrieve', })
		response = aview(request, pk=1)

		assert response.status_code == 403, \
			"It disallows, if action authorizer at model is absent."


	# def test6(self):
	# 	assert 0, "It automatically resolves serializer based upon requested resource version."

# class TestSaneModelAPI:
	# def test7(self):
	# 	assert 0, "It disables PUT by default."

	# def test8(self):
	# 	assert 0, "It throws if filter_queryset() is not implemented."


# class TestSaneSerializer:
	# def test_get_readable_fields(self):
	# 	assert 0, "It is called during deserialization."

	# def test_get_writable_fields(self):
	# 	assert 0, "It is called during serialization."

	# def test__init__(self):
	# 	assert 0, "It writes subset of allowed fields."
	# 	assert 0, "It reads subset of allowed fields."

	# # assert "Above nature is recursive."


# class TestSaneAPITester:
	# def test1(self):
	# 	assert 0, "It warns about apis which do not implement Sane api."

# class TestSaneSerializerTester:
	# def test1(self):
	# 	assert 0, "It warns about serializers which do not implement Sane api."


# # # user can override this method if does not like it, same goes for get_readable_fields at serializer
# # def can_<action>:
# #     execute <role>_can_<actin>


# # authorizer method signature api
# # Viewset.can_retrieve()
# # Viewset.admin_can_retrieve()
# # Viewset.consumer_can_retrieve()


# # authorizer method signature at model
# # Model.can_retrieve()

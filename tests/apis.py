from unittest.mock import patch

from django.test import TestCase
from django.db import models

from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import detail_route, list_route

from sane_api.apis import SaneAPIMixin, SaneAPI, SaneModelAPI, HelperAPI

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

	def get_queryset(self):
		return self.queryset

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

	def test5(self):
		delattr(ASaneModelAPI, "get_queryset")
		request = factory.get('/', '', content_type='application/json')
		aview = ASaneModelAPI.as_view(actions= {'get': 'retrieve', })

		try:
			response = aview(request, pk=1)
			assert 0, "It should throw if get_queryset() is not implemented."
		except Exception as e:
			pass

class TestSaneAPITester:
	def test1(self):
		assert 0, "It warns about apis which do not implement Sane api."

class TestHelperAPI(APITestCase):
	def setup_compose(self):
		from tests.urls import urlpatterns
		from rest_framework import routers

		class LocationAPI(SaneAPI):
			@list_route(methods=["get"])
			def location1(self, request):
				data = { "id": 1 , "name": "location 1" }
				return Response(data, status=200)

			def can_location1(self, user, request):
				return True

			@list_route(methods=["get"])
			def location2(self, request):
				data = \
						[
								{ "id": 2, "name": "location 2", "parent": 1},
								{ "id": 3, "name": "location 2", "parent": 2},
								{ "id": 4, "name": "location 2", "parent": 1},
						]
				parent = request.query_params.get("parent")
				if parent:
					filtered_data = filter(lambda adata: parent == str(adata["parent"]), data)
				else:
					filtered_data = []
				return Response(filtered_data, status=200)

			def can_location2(self, user, request):
				return True

			@list_route(methods=["get"])
			def location3(self, request):
				print(request.query_params.get("id"))
				return Response(request.query_params.get("id", []), status=200)

			def can_location3(self, user, request):
				return True

		router = routers.SimpleRouter()
		router.register("location", LocationAPI, base_name="location")
		router.register("helper", HelperAPI, base_name="helper")

		urlpatterns.extend(router.urls)

	def test_compose1(self):
		from django.core.urlresolvers import reverse
		self.setup_compose()

		payload = \
				{ "location1": {"url": "/location/location1/"}
				, "location2": {"url": "/location/location2/"}
				, "location3": {"url": "/location/location3/"}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		expected = \
				{ "location1":{"id":1,"name":"location 1"}
				, "location2":[]
				, "location3":[]
				}
		assert response.json() == expected, "It works for urls without dependency."

	def test_compose2(self):
		from django.core.urlresolvers import reverse
		self.setup_compose()

		payload = \
				{ "location1": {"url": "/location/location1/"}
				, "location2": \
						{ "url": "/location/location2/"
						, "query": {"parent": "{location1.id}"}
						}
				, "location3": \
						{ "url": "/location/location3/"
						, "query": {"id": "{location2.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		expected = \
				{ "location1":{"id":1,"name":"location 1"}
				, "location2":[
						{ "id": 2, "name": "location 2", "parent": 1},
						{ "id": 4, "name": "location 2", "parent": 1},
					]
				, "location3": "2,4"
				}
		assert response.json() == expected, "It works for urls with dependency."

	def test_compose3(self):
		from django.core.urlresolvers import reverse
		self.setup_compose()

		payload = \
				{ "location1": {"url": "/location/location1/"}
				, "location2": \
						{ "url": "/location/location2/"
						, "query": {"parent": "{location3.id}"}
						}
				, "location3": \
						{ "url": "/location/location3/"
						, "query": {"id": "{location2.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, "It complains if urls have cyclic dependency."
		assert "location2" or "location3" in response.json()["detail"]

	def test_compose4(self):
		from django.core.urlresolvers import reverse
		self.setup_compose()

		payload = \
				{ "location1": {"url": "/location/location1/"}
				, "location2": \
						{ "url": "/location/location2/"
						, "query": {"parent": "{location3.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, \
				"It complains if a url has unmet dependecy at root level."
		assert "location3" in response.json()["detail"]

	def test_compose5(self):
		from django.core.urlresolvers import reverse
		self.setup_compose()

		payload = \
				{ "location1": {"url": "/location/location1/"}
				, "location2": \
						{ "url": "/location/location2/"
						, "query": {"parent": "{location1.nokey}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, \
				"It complains if a url has unmet dependecy at sub level."
		assert "location1.nokey" in response.json()["detail"]

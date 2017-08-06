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
	def setUp(self):
		from tests.urls import urlpatterns
		from rest_framework import routers

		class BlogAPI(SaneAPI):
			@list_route(methods=["get"])
			def user(self, request):
				data = \
						[
							{ "id": 1 , "name": "user1" },
							{ "id": 2 , "name": "user2" },
							{ "id": 3 , "name": "user3" },
						]
				user_id = request.query_params.get("id")
				if user_id:
					filtered_data = list(filter(lambda adata: str(adata["id"]) == user_id, data))
				else:
					filtered_data = data
				return Response(filtered_data, status=200)

			def can_user(self, user, request):
				return True

			@list_route(methods=["get"])
			def article(self, request):
				data = \
						[
								{ "id": 1, "user": 1, "title": "article1"},
								{ "id": 2, "user": 1, "title": "article2"},
								{ "id": 3, "user": 2, "title": "article3"},
						]
				user = request.query_params.get("user")
				if user:
					filtered_data = \
							list(filter(lambda adata: str(adata["user"]) in user.split(","), data))
				else:
					filtered_data = data
				return Response(filtered_data, status=200)

			def can_article(self, user, request):
				return True

			@list_route(methods=["get"])
			def comment(self, request):
				data = \
						[
								{ "id": 1, "user": 1, "article": 1, "title": "comment1"},
								{ "id": 2, "user": 1, "article": 2, "title": "comment2"},
								{ "id": 3, "user": 2, "article": 3, "title": "comment3"},
						]

				user = request.query_params.get("user")
				article = request.query_params.get("article")

				filtered_data = \
						list(filter(
								lambda adata: \
										str(adata["user"]) in user.split(",") \
										and str(adata["article"]) in article.split(",")
										, data))
				return Response(filtered_data, status = 200)

			def can_comment(self, user, request):
				return True

		router = routers.SimpleRouter()
		router.register("blog", BlogAPI, base_name="blog")
		router.register("helper", HelperAPI, base_name="helper")

		urlpatterns.extend(router.urls)

	def tearDown(self):
		from tests.urls import urlpatterns
		del urlpatterns[:]

	def test_compose1(self):
		from django.core.urlresolvers import reverse

		payload = \
				{ "user": {"url": "/blog/user/"}
				, "article": {"url": "/blog/article/"}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		expected = \
				{ "user": [
						{ "id": 1 , "name": "user1" },
						{ "id": 2 , "name": "user2" },
						{ "id": 3 , "name": "user3" },
					]
					, "article": [
							{ "id": 1, "user": 1, "title": "article1"},
							{ "id": 2, "user": 1, "title": "article2"},
							{ "id": 3, "user": 2, "title": "article3"}
					]
				}
		assert response.json() == expected, "It works for urls without dependency."


	def test_compose2(self):
		from django.core.urlresolvers import reverse

		payload = \
				{ "user": {"url": "/blog/user/", "query": {"id": 1}}
				, "article": \
						{ "url": "/blog/article/"
						, "query": {"user": "{user.id}"}
						}
				, "comment": \
						{ "url": "/blog/comment/"
						, "query": {"article": "{article.id}", "user": "{user.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		expected = \
				{ "user": [
						{ "id": 1 , "name": "user1" }
					]
				, "article": [
						{ "id": 1, "user": 1, "title": "article1"},
						{ "id": 2, "user": 1, "title": "article2"},
					]
				, "comment": [
						{ "id": 1, "user": 1, "article": 1, "title": "comment1"},
						{ "id": 2, "user": 1, "article": 2, "title": "comment2"},
					]
				}
		assert response.json() == expected, "It works for urls with dependency."


	def test_compose3(self):
		from django.core.urlresolvers import reverse

		payload = \
				{ "user": {"url": "/blog/user/"}
				, "article": \
						{ "url": "/blog/article/"
						, "query": {"parent": "{comment.id}"}
						}
				, "comment": \
						{ "url": "/blog/comment/"
						, "query": {"id": "{article.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, "It complains if urls have cyclic dependency."
		assert "article" or "comment" in response.json()["detail"]


	def test_compose4(self):
		from django.core.urlresolvers import reverse

		payload = \
				{ "user": {"url": "/blog/user/"}
				, "article": \
						{ "url": "/blog/article/"
						, "query": {"comment": "{comment.id}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, \
				"It complains if a url has unmet dependecy at root level."
		assert "comment" in response.json()["detail"]


	def test_compose5(self):
		from django.core.urlresolvers import reverse

		payload = \
				{ "user": {"url": "/blog/user/"}
				, "article": \
						{ "url": "/blog/article/"
						, "query": {"user": "{user.nokey}"}
						}
				}
		url = reverse("helper-compose")
		response = self.client.post(url, payload, format="json")	

		assert response.status_code == 400, \
				"It complains if a url has unmet dependecy at sub level."
		assert "user.nokey" in response.json()["detail"]


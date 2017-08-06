from django.test import TestCase

from sane_api.helpers import \
		( get_cyclic_dependency
		, get_unmet_dependency
		, get_value_at
		, fill_template
		)
from sane_api.exceptions import UnmetDependency


class TestHasCyclicDependency(TestCase):
	def test1(self):
		data = \
				{ "article": {"query": {"comment": "{comment.id}", "user": "{user.id}"}}
				, "user": {"query": {"articles": "{article.id}"}}
				, "comment": {"query": {}}
				}
		assert get_cyclic_dependency(data) in ["article", "user"], \
				"Returns the key at which cyclic dependency exists."

	def test2(self):
		data = \
				{ "article": {"query": {"user": "{user.id}", "comment": "{comment.id}"}}
				, "user": {"query": {"id": 1}}
				, "comment": {"query": {}}
				}
		assert get_cyclic_dependency(data) == None, \
				"Returns None if has no cyclic dependency."


class TestHasUnmetDependency(TestCase):
	def test1(self):
		data = \
				{ "user": {"query": {}}
				, "article": {"query": {"comment": "{comment.id}", "user": "{user.id}"}}
				}
		assert get_unmet_dependency(data) == ["article", "comment"], \
				"Returns the key which has unmet dependency."

	def test2(self):
		data = \
				{ "user": {"query": {}}
				, "article": {"query": {"user": "{user.id}"}}
				}
		assert get_unmet_dependency(data) == None, \
				"Returns None if has no unmet dependency."

class TestGetValueAt(TestCase):
	def test1(self):
		path = ["user", "id"]
		source = { "user": {"id": 1}}
		assert get_value_at(path, source, start=True) == 1, \
				"It returns value from single object at given path."

	def test2(self):
		path = ["user", "id"]
		source = \
				[
					{ "user": {"id": 1}},
					{ "user": {"id": 2}}
				]
		assert get_value_at(path, source, start=True) == "1,2", "It return value from list at given path."

		path = ["user", "id"]
		source = { "user": [{"id": 1}, {"id": 2}]}
		assert get_value_at(path, source, start=True) == "1,2", "It return value from list at given path."

	def test3(self):
		path = ["user", "username"]
		source = { "user": {"id": 1}}
		try:
			get_value_at(path, source, start=True)
			assert 0, "It should have thrown UnmetDependency."
		except UnmetDependency:
			pass

class TestFillTemplate(TestCase):
	def test1(self):
		req_sig = \
				{ "url": "/api/comment/"
				, "query": {"user": "{user.id}", "article": "{article.id}"}
				}
		source = { "user": [{"id": 1}, {"id": 2}], "article": {"id": 1}}
		expected = \
				{ "url": "/api/comment/"
				, "query": {"user": "1,2", "article": "1"}
				}
		assert fill_template(req_sig, source) == expected, \
				"It fills the template and returns filled request signature."

	def test2(self):
		req_sig = \
				{ "url": "/api/comment/"
				, "query": {"user": "{user.id}", "article": "{x.id}"}
				}
		source = { "user": [{"id": 1}, {"id": 2}], "article": {"id": 1}}
		expected = \
				{ "url": "/api/comment/"
				, "query": {"user": "1,2", "article": "1"}
				}
		assert fill_template(req_sig, source) == None, \
				"It returns None template could not be filled due to unresolved dependency."

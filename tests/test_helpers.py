from django.test import TestCase

from sane_api.helpers import get_cyclic_dependency, get_unmet_dependency


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

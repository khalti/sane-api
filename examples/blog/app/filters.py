from app.models import Article, Comment
from sane_api.filters import SaneFilterSet


class ArticleFilterSet(SaneFilterSet):
	def get_filterables(self):
		return \
				{ "created_on": ["exact", "lt"]
				, "modified_on": ["lt", "gt"]
				, "title": ["exact", "istartswith", "iendswith"]
				};

	class Meta:
		model = Article
		fields = '__all__'


class CommentFilterSet(SaneFilterSet):
	def get_filterables(self):
		return \
				{ "id": ["exact", "in"]
				, "article": ["exact", "in"]
				}

	class Meta:
		model = Comment
		fields = '__all__'

from sane_api.apis import SaneModelAPI
from app.serializers import ArticleSerializer, CommentSerializer
from app.models import Article, Comment
from app.filters import ArticleFilterSet, CommentFilterSet


class ArticleAPI(SaneModelAPI):
	queryset = Article.objects.all()
	serializer_class = ArticleSerializer
	filter_class = ArticleFilterSet

	def get_queryset(self):
		return self.queryset

	def can_list(self, user, request):
		return True

	def can_retrieve(self, user, request):
		return True


class CommentAPI(SaneModelAPI):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
	filter_class = CommentFilterSet

	def get_queryset(self):
		return self.queryset

	def can_list(self, user, request):
		return True

	def can_retrieve(self, user, request):
		return True

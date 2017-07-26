from sane_api.apis import SaneModelAPI
from app.serializers import ArticleSerializer, CommentSerializer
from app.models import Article, Comment


class ArticleAPI(SaneModelAPI):
	queryset = Article.objects.all()
	serializer_class = ArticleSerializer

	def get_queryset(self):
		return self.queryset

	def can_list(self, user, request):
		return True


class CommentAPI(SaneModelAPI):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def get_queryset(self):
		return self.queryset

	def can_list(self, user, request):
		return True

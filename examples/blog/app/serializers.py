from sane_api.serializers import SaneModelSerializer
from app.models import Article, Comment


class ArticleSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		return ["title", "body", "user", "created_on", "modified_on"]

	class Meta:
		model = Article
		fields = "__all__"


class CommentSerializer(SaneModelSerializer):
	article = ArticleSerializer()

	def get_readable_fields(self):
		return ["content", "article", "user", "created_on", "modified_on"]

	class Meta:
		model = Comment
		fields = "__all__"

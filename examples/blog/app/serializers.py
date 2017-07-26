from sane_api.serializers import SaneModelSerializer
from app.models import Article, Comment

class CommentSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		return ["content", "article", "user", "created_on", "modified_on", "id"]

	class Meta:
		model = Comment
		fields = "__all__"

class ArticleSerializer(SaneModelSerializer):
	comments = CommentSerializer(many=True)

	def get_readable_fields(self):
		return ["title", "body", "user", "created_on", "modified_on", "comments"]

	class Meta:
		model = Article
		fields = "__all__"


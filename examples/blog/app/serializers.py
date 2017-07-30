from django.contrib.auth import get_user_model

from sane_api.serializers import SaneModelSerializer
from app.models import Article, Comment

User = get_user_model()

class UserSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		user = self.context["request"].user
		if user.is_superuser:
			return ["username", "first_name", "last_name", "is_staff", "is_superuser", "is_active"]

		return ["username", "first_name", "last_name", "is_active"]

	def get_writable_fields(self):
		user = self.context["request"].user
		if user.is_superuser:
			return ["username", "first_name", "last_name", "is_staff", "is_superuser", "is_active"]

		return ["first_name", "last_name"]

	class Meta:
		model = User
		fields = "__all__"

class CommentSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		return ["content", "article", "user", "created_on", "modified_on", "id"]

	class Meta:
		model = Comment
		fields = "__all__"

class ArticleSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		return ["id", "title", "body", "user", "created_on", "modified_on", "comments"]

	class Meta:
		model = Article
		fields = "__all__"


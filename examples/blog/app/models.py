from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseModel(models.Model):
	created_on = models.DateTimeField(auto_now=True)
	modified_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True
	
class Article(BaseModel):
	title = models.CharField(max_length=100)
	body = models.CharField(max_length=1000)
	user = models.ForeignKey(User, related_name="posts")

	def can_retrieve(self, user, request):
		return True

class Comment(BaseModel):
	content = models.CharField(max_length=200)
	article = models.ForeignKey(Article, related_name="comments")
	user = models.ForeignKey(User, related_name="comments")

	def can_retrieve(self, user, request):
		return True

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class BaseModel(models.Model):
	created_on = models.DateTimeField(auto_now=True)
	modified_on = models.DateTimeField(auto_now_add=True)
	
class Post(BaseModel):
	title = models.CharField(max_length=100)
	body = models.CharField(max_length=1000)
	user = models.ForeignKey(User, related_name="posts")

class Comment(BaseModel):
	content = models.CharField(max_length=200)
	post = models.ForeignKey(Post, related_name="comments")

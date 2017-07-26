from django.contrib import admin
from app.models import Article, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	pass

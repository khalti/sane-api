> Project is still flux.

## Introduction
Sane API is an opinionated, secure and scalable framework built on top of `Django REST Framework`.

## Features
- secure by default apis
- field level serialization control
- field level filteration control
- composable apis (hit multiple apis at once)

## View
### Problems
1. permission management is complex and hard
2. accidental expose of api

### Solution
1. implement action based permissions
2. make apis inaccessible by default

Sane API enforces action level authentication. It provides `SaneAPI` and `SaneModelAPI`.
Extend `SaneModelAPI` and `SaneAPI` for viewsets which have and do not have `queryest` respectively.
`By default every actions of viewset that extends them are inaccisible.`
So that even if one forgets to implement authentication logics for the actions, they do not
get exposed.

There are two level of authorization:

To illustrate the concepts lets take following code as an example.

```python
class Article(models.Model):
	author = models.ForeignKey(User)
	# ... model fields here

	def can_update(self, user, request):
		if self.author == user:
			return True

class ArticleAPI(SaneModelAPI):
	def update (self, request):
		# logics here
		pass
	
	def can_update(self, user, request):
		if user.belongs_to("Author"):
			return True
```

### 1. API level
For every action there must be corresponding authorizer at the viewset.
In the example above `update` action is only accissible if `can_update` authorizer at `ArticleAPI` viewset returns `True`.

### 2. Object level
Every action which deals with a model instance must implement an authorizer at the model.
In the example above an article can only be updated if `can_update` authorizer at `Article`
model returns `True`.

## Serializer
### Problems
- different users/groups have different level of access to readable and writable fields
- maintaining multiple serializers for different users/groups or apis is complex and difficult to maintain

### Solution
- let serializer return readable and writable fields based upon users/groups.

Every new serializer must extend `SaneSerializer` or `SaneModelSerializer`.
Extend `SaneModelSerializer` for serializing model instances else extend `SaneSerializer`.

Every new serializer must implement `get_readable_fields` and `get_writable_fields` else
`Sane api` will complain about it.

### get_readable_fields
This method must conditionally return readable fields.
Implement this method to return different fields for different user/group.

```python
class ArticleSerializer(SaneModelSerializer):
	def get_readable_fields(self):
		user = self.context.get("request").user
		if user.belongs_to("Admin"):
			return ["user", "title", "content", "created_on", "modified_on"]
		elif user.belong_to("Author"):
			return ["title" "content", "created_on", "modified_on"]

	class Meta:
		model = Article
		fields = '__all__'
```

### get_writable_fields
This method must conditionally return writable fields.
Implement this method to return different fields for different user/group.

```python
class ArticleSerializer(SaneModelSerializer):
	def get_writable_fields(self):
		user = self.context.get("request").user
		if user.belongs_to("Admin"):
			return ["user", "title", "content", "created_on", "modified_on"]
		elif user.belong_to("Author"):
			return ["title" "content"]

	class Meta:
		model = Article
		fields = '__all__'
```

## Filter
### Problem
- different users/groups have different level of filtration access
- implementing multiple filter classes for user/groups is complex and difficult to maintain

### Solution
- allow developer to return filteration 

Sane api provides `SaneFilterSet`. One must implement `get_filterables` to return differnt
filterset for different user/group.

```python
class ArticleFilterSet(SaneFilterSet):
	def get_filterables(self):
		# get current user
		if user.belongs_to("Admin"):
			return \
					{ "user": ["exact"]
					, "title": ["exact", "istartswith", "iendswith"]
					, "created_on": ["exact", "lt", "gt"]
					, "modified_on": ["exact", "lt", "gt"]
					};
		elif user.belongs_to("Author"):
			return \
					{ "title": ["exact", "istartswith", "iendswith"]
					, "created_on": ["exact", "lt", "gt"]
					};

	class Meta:
		model = Article
		fields = '__all__'
```

## Composite api
### Problem
- making multiple network calls is inefficient and hard for clients to handle

### Solution
- facilitate client to fetch data from multiple apis through single api request

With `Sane API` one can fetch data from multiple apis through single request using `HelperAPI.compose()` action.
It must be hooked to `DRF` router before use.

There are two ways compose apis:

### 1. Dependent apis
Imagine a situation where one need to fetch list of users and their articles.
In this situation, articles are dependent to the users. Below is the example to fetch
dependent data.

```python
import requests

url = "http://somewhere.com/api/compose/"
payload = {
	"user": {"url": "http://somewhere.com/api/user/"},
	"article": {
		"url": "http://somewhere.com/api/article/",
		"params": {"user": "{{user.id}}"}
		}
}
response = requests.post(url, payload)
# response.data == {user: [...], article: [...]}
```

### 2. Independent apis
...

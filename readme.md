Project is still flux.

## Introduction
sane-api

## Features
- secure by default apis
- field level serialization control
- field level filteration control
- composible apis (hit multiple apis at once)

## View
Sane api inforces action level authentication. It provides `SaneAPI` and `SaneModelAPI`.
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
Every new serializer must extend `SaneSerializer` or `SaneModelSerializer`.
Extend `SaneModelSerializer` for serializing model instances else extend `SaneSerializer`.

Every new serializer must implement `get_readable_fields` and `get_writable_fields` else
`Sane api` will throw an exception complaning about it.

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
- independent compose
- dependent compose

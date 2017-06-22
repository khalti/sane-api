class TestSaneAPIMixin:
	def test1(self):
		assert 0, "It implements action based api level permission by default."

	def test2(self):
		assert 0, "It implements action based object level permission."

	def test3(self):
		assert 0, "It throws 403, if the action handler is undefined."

	def test4(self):
		assert 0, "It throws 403, if the action handler returns undefined."

	def test5(self):
		assert 0, "If throws 403, if the action handler returns false."

	def test6(self):
		assert 0, "It automatically resolves serializer based upon requested resource version."

class TestSaneModelAPI:
	def test7(self):
		assert 0, "It disables PUT by default."

	def test8(self):
		assert 0, "It throws if filter_queryset() is not implemented."


class TestSaneSerializer:
	def test_get_readable_fields(self):
		assert 0, "It is called during deserialization."

	def test_get_writable_fields(self):
		assert 0, "It is called during serialization."

	def test__init__(self):
		assert 0, "It writes subset of allowed fields."
		assert 0, "It reads subset of allowed fields."

	# assert "Above nature is recursive."


class TestSaneAPITester:
	def test1(self):
		assert 0, "It warns about apis which do not implement Sane api."

class TestSaneSerializerTester:
	def test1(self):
		assert 0, "It warns about serializers which do not implement Sane api."


# # user can override this method if does not like it, same goes for get_readable_fields at serializer
# def can_<action>:
#     execute <role>_can_<actin>


# authorizer method signature api
# Viewset.can_retrieve()
# Viewset.admin_can_retrieve()
# Viewset.consumer_can_retrieve()


# authorizer method signature at model
# Model.can_retrieve()

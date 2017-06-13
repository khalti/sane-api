class TestSaneAPI:
    def test1(self):
        assert 0, "It implements role-action based api level permission by default."

    def test2(self):
        assert 0, "It implements role-action based object level permission."

    def test3(self):
        assert 0, "It throws 403, if the action handler is undefined."

    def test4(self):
        assert 0, "It throws 403, if the action handler returns undefined."

    def test5(self):
        assert 0, "If throws 403, if the action handler returns false."

    def test6(self):
        assert 0, "It automatically resolves serializer based upon requested resource version."

    def test7(self):
        assert 0, "It disables PUT by default."

    def test8(self):
        assert 0, "It supports role based queryset."


class TestSaneSerializer:
    def test_get_readable_fields(self):
        assert 0, "It is called during deserialization."

    def test_get_writable_fields(self):
        assert 0, "It is called during serialization."

    def test__init__(self):
        assert 0, "It writes subset of allowed fields."
        assert 0, "It reads subset of allowed fields."


class TestSaneAPITester:
    def test1(self):
        assert 0, "It warns about apis which do not implement Sane api."

class TestSaneSerializerTester:
    def test1(self):
        assert 0, "It warns about serializers which do not implement Sane api."


# # user can override this method if does not like it, same goes for get_readable_fields at serializer
# def can_<action>:
#     execute <role>_can_<actin>

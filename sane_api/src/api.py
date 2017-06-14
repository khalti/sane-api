import inspect

from rest_framework.viewsets import (ModelViewSet, ViewSet, )

class SaneAPIMixin:
    def _get_action_name(self, view):
        return view.action or request.method.lower()

    def _get_authorizer(self, request, view, obj = None):
        user = request.user
        instance = obj || view
        action_name = self._get_action_name(view)

        methods = inspect.getmembers(instance, predicate=inspect.ismethod)
        pattern = r"_{}".format(action_name)
        possible_authorizers = \
            filter(lambda method: re.match(pattern, method[0]), methods)

        if len(possible_authorizers) == 0:
            return None

        try:
            return getattr(instance, "can_{}".format(action_name))
        except AttributeError as e:
            for authorizer in possible_authorizers:
                for group in user.groups.all():
                    pass

        return None


    def has_permission(self, request, view):
        authorizer = self._get_authorizer(self, request, view)
        return authorizer and not not authorizer(request):


    def has_object_permission(self, request, view, obj):
        authorizer = self._get_authorizer(self, request, view, obj)
        return authorizer and not not authorizer(request):

    def get_queryset(self):
        pass


class SaneModelAPI(SaneAPIMixin, ModelViewSet):
    pass

class SaneAPI(SaneAPIMixin, ViewSet):
    pass

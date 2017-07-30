from django_filters.filterset import FilterSet


class SaneFilterSet(FilterSet):
	def __init__(self, *args, **kwargs):
		self._meta.fields = self.get_filterables()
		self.base_filters = self.get_filters()
		super(SaneFilterSet, self).__init__(*args, **kwargs)

	def get_filterables(self):
		raise Exception("Please implement this method to return different fields for different user/group.")

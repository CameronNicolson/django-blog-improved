from blog_improved.query_request.query import QueryRequestDecorator

class SortQueryRequest(QueryRequestDecorator):
    def __init__(self, queryset_request=None, sort_by=None, priority=10):
        """
        Initialize the SortQueryRequest class.

        :param queryset_request: The QueryRequest object to decorate.
        :param sort_by: A list or tuple of fields to sort by, e.g., ['-created_at', 'name'].
        :param priority: Priority for applying this sort in the request pipeline.
        """
        super().__init__(queryset_request=queryset_request)

        if not sort_by or not isinstance(sort_by, (list, tuple)):
            raise ValueError("You must provide a 'sort_by' parameter as a list or tuple.")

        self._sort_by = sort_by
        self._priority = priority

    def make_request(self):
        """
        Apply the sorting to the QuerySet.
        """
        sort_method = ("order_by", tuple(self._sort_by), {}, self._priority)
        self.get_request().get_methods().append(sort_method)

        return self._queryset_request.make_request()

from django.db.models.query import QuerySet
from django.apps import apps

class QueryRequest:
    def __init__(self, app_name, model, methods, return_type="instances"):
        self._app_name = app_name
        self._model = apps.get_model(app_name, model)
        self._selected_fields = set()
        for method in methods:
            obj = QuerySet
            method_name, _, _, _ = method
            if hasattr(obj, method_name) == False:
                raise AttributeError("%s is not an attribute of %s." % (method_name, obj.__name__))
        self._methods:list[tuple] = methods or list() 
        self._return_type = return_type
        self._cache = None
  
    def set_return_type(self, return_type, fields=None):
        """Set the desired return type and fields."""
        self._return_type = return_type
        self._selected_fields = self._selected_fields or []

    def get_methods(self):
        return self._methods

    def add_selected_fields(self, fields):
        """Add selected fields."""
        self._selected_fields.extend(fields)

    def get_selected_fields(self):
        """Get currently selected fields."""
        return list(self._selected_fields)

    def make_request(self) -> QuerySet:
        if self._cache is not None:
            return self._cache

        # Sort methods by priority (lowest number = higher priority)
        sorted_methods = sorted(self._methods, key=lambda x: x[3])
        qs = QuerySet(model=self._model)
        for method in sorted_methods:
            prev_qs = qs
            method_name, args, kwargs, _ = method
            if args is None and kwargs is None:
                new_qs = getattr(qs, method_name)()
            else:
                new_qs = getattr(qs, method_name)(*args, **kwargs)
            qs = new_qs if isinstance(new_qs, QuerySet) else prev_qs

        self._cache = qs  # Cache the resulting QuerySet

        return qs

    def evaluate(self):
        """Evaluate the QuerySet with the return type applied."""
        qs = self.make_request()  # Get the QuerySet (cached if already executed)

        # Apply the return type lazily, just before evaluation
        if self._return_type == "values":
            return qs.values(*self._selected_fields)
        elif self._return_type == "values_list":
            return qs.values_list(*self._selected_fields)
        return qs  # Default is "instances" (no transformation)

class QueryRequestDecorator: 
    def __init__(self, queryset_request=None):
        self._queryset_request = queryset_request

    def get_methods(self):
        return self._queryset_request.get_methods()

    def get_request(self):
        return self._queryset_request

    def make_request(self):
        self._queryset_request.make_request()

    def __getattr__(self, name):
        """Delegate missing attributes/methods to the wrapped request."""
        return getattr(self._queryset_request, name)

class QueryRequestSelectValues(QueryRequestDecorator):
    def __init__(self, queryset_request=None, fields=None, priority=2):
        super().__init__(queryset_request=queryset_request)
        self._fields = fields or set()
        self._priority = priority

    def make_request(self):
        select_method = ("only", self._fields, {}, self._priority)
        self._queryset_request.get_methods().append(select_method)
        self.get_request().add_selected_fields(self._fields)
        qs = self._queryset_request.make_request()
        return qs

class FilterQueryRequest(QueryRequestDecorator):
    def __init__(self, queryset_request=None, negate=False, lookup_field=None, lookup_transformers=[], lookup_type="exact", lookup_value=None, inner_join=None, priority=1):
        super().__init__(queryset_request=queryset_request)
        self._negate = negate
        self._lookup_field = lookup_field
        self._lookup_transformers = lookup_transformers
        self._lookup_type = lookup_type
        self._lookup_value = lookup_value
        self._inner_join = inner_join
        self._priority = priority

    def apply_inner_join(self):
        select_related = ("select_related", self._inner_join, {}, self._priority)
        self.get_request().get_methods().append(select_related)
    
    def get_field_lookup(self):
        lookup_lhs = self._lookup_field
        lookup_rhs = self._lookup_value
        if not lookup_rhs:
            return None
        transformers = self._lookup_transformers
        transformers = transformers if isinstance(transformers, list) else [transformers]
        for lookup_part in transformers:
            if lookup_part:
                lookup_lhs += "__" + str(lookup_part)
        if isinstance(lookup_rhs, list):
            self._lookup_type = "in" 
        lookup_lhs += "__%s" % self._lookup_type
        return {lookup_lhs: lookup_rhs}

    def make_request(self):
        lookup = self.get_field_lookup()
        if self._inner_join:
            self.apply_inner_join()
        if lookup:
            method_name = "filter" if self._negate == False else "exclude" 
            new_method = (method_name, tuple(), lookup, self._priority,)
            self.get_request().get_methods().append(new_method)
        qs = self._queryset_request.make_request()
        return qs

class LimitQueryRequest(QueryRequestDecorator):
    def __init__(self, queryset_request=None, max_limit=None, offset=None, priority=20):
        super().__init__(queryset_request=queryset_request)
        if not isinstance(max_limit, int) or (offset is not None and not isinstance(offset, int)):
            raise TypeError("The limit and offset values must be integers.")
        if max_limit < 0 or (offset is not None and offset < 0):
            raise ValueError("Negative integers are not allowed for limit or offset.")
        self._max_limit = max_limit
        self._offset = offset
        self._priority = priority
  
    def make_request(self): 
        limit = self._max_limit
        start = self._offset if self._offset else 0
        stop = self._max_limit
        slicing_args = (slice(start, stop),)
        limit_method = ("__getitem__", slicing_args, {}, self._priority)
        self.get_request().get_methods().append(limit_method)
        return self._queryset_request.make_request()


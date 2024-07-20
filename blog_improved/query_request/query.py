from django.db.models.query import QuerySet
from django.apps import apps

class QuerySetRequest:
    def __init__(self, app_name, model, methods):
        self._app_name = app_name
        self._model = apps.get_model(app_name, model)
        for method in methods:
            obj = QuerySet
            method_name, _, _ = method
            if hasattr(obj, method_name) == False:
                raise AttributeError("%s is not an attribute of %s." % (method_name, obj.__name__))
        self._methods:list[tuple] = methods or list() 
   
    def get_methods(self):
        return self._methods

    def make_request(self) -> QuerySet:
        qs = QuerySet(model=self._model)
        for method in self._methods:
            prev_qs = qs
            method_name, args, kwargs = method
            if args is None and kwargs is None:
                new_qs = getattr(qs, method_name)()
            else:
                new_qs = getattr(qs, method_name)(*args, **kwargs)
            qs = new_qs if isinstance(new_qs, QuerySet) else prev_qs
        return qs

class QuerySetRequestDecorator: 
    def __init__(self, queryset_request=None):
        self._queryset_request = queryset_request

    def get_methods(self):
        return self._queryset_request.get_methods()

    def get_request(self):
        return self._queryset_request

    def make_request(self):
        self._queryset_request.make_request()

class QuerySetRequestSelectValues(QuerySetRequestDecorator):
    def __init__(self, queryset_request=None, fields=()):
        super().__init__(queryset_request=queryset_request)
        self._fields = fields

    def make_request(self):
        select_method = ("only", self._fields, {},)
        self._queryset_request.get_methods().append(select_method)
        self._queryset_request.make_request()

class FilterQuerySetRequest(QuerySetRequestDecorator):
    def __init__(self, queryset_request=None, negate=False, lookup_field=None, lookup_transformers=[], lookup_type="exact", lookup_value=None):
        super().__init__(queryset_request=queryset_request)
        self._negate = negate
        self._lookup_field = lookup_field
        self._lookup_transformers = lookup_transformers
        self._lookup_type = lookup_type
        self._lookup_value = lookup_value
    
    def get_field_lookup(self):
        lookup_lhs = self._lookup_field
        transformers = self._lookup_transformers
        transformers = transformers if isinstance(transformers, list) else [transformers]
        for lookup_part in transformers:
            if lookup_part is not None:
                lookup_lhs += "__" + str(lookup_part)
        lookup_lhs += "__%s" % self._lookup_type
        lookup_rhs = self._lookup_value
        return {lookup_lhs: lookup_rhs}

    def make_request(self):
        lookup = self.get_field_lookup()
        method_name = "filter" if self._negate == False else "exclude" 
        new_method = (method_name, tuple(), lookup,)
        self.get_request().get_methods().append(new_method)
        qs = self._queryset_request.make_request()
        return qs


from django import template
from django.db.models.query import QuerySet
from blog_improved.models import Post, Status
from blog_improved.utils.strings import convert_str_kwargs_to_list
from blog_improved.query_request.query import QuerySetRequest, FilterQuerySetRequest

register = template.Library()

bloglist_args_mapping = {
    "category": {
        "FilterQuerySetRequest": {
            "negate": False,
            "lookup_field": "category",
            "lookup_type": "exact",
            "lookup_value": None
        }
    },
    "ignore-category": {
        "FilterQuerySetRequest": {
            "negate": True,
            "lookup_field": "category",
            "lookup_type": "exact",
            "lookup_value": None
        }
    },
    "visibility": {
        "FilterQuerySetRequest": {
            "negate": False,
            "lookup_field": "status",
            "lookup_type": "exact",
            "lookup_value": None
        }
    }

}

decorator_registry = {
        "FilterQuerySetRequest": FilterQuerySetRequest
}

def apply_sequence_queryset_request(instance: QuerySetRequest, requests_to_apply:list):
    queryset_request = instance
    for request in requests_to_apply:
        for classname, class_kwargs in request.items():
            class_ref = decorator_registry.get(classname)
            if class_ref:
                decorator = class_ref(queryset_request=queryset_request, **class_kwargs)
                queryset_request = decorator
    return queryset_request

def translate_kwargs(tag_kwargs):
    translated_kwargs = []
    for tag_key, tag_value in tag_kwargs.items():
        list_classes = bloglist_args_mapping.get(tag_key) or iter([])
        for class_key, class_vals in list_classes.items():
            new_kwargs = dict((k, tag_value) if None else (k, v) for k, v in class_vals.items() ) 
            translated_kwargs.append({class_key: new_kwargs})
    return translated_kwargs


@convert_str_kwargs_to_list
def bloglist(*args, **kwargs):
    # add visibility if not provided by tag
    if kwargs.get("visibility") == None:
        kwargs["visibility"] = Status.name_to_id("publish")
 
    requests = translate_kwargs(kwargs)
    initial_request = QuerySetRequest("blog_improved", "Post", [])
    bob = apply_sequence_queryset_request(initial_request, requests) 
    return {} 

def querysetfilter(func):
    """
    Decorator for filters which should only receive querysets. The object
    passed as the first positional argument will be type checked.
    """
    def _dec(first, *args, **kwargs):
        if isinstance(first, QuerySet) and not isinstance(first, EmptyQuerySet):
            result = func(first, *args, **kwargs)
        return result

    return _dec

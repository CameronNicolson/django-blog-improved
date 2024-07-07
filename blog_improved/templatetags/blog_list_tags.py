from django import template
from django.db.models.query import QuerySet
from blog_improved.models import Post

register = template.Library()

@register.simple_tag
def bloglist(*args, **kwargs):
    _model = kwargs.get("model", None) or Post
    _manager = Post.public
    query = QuerySet.__new__(QuerySet)
    query.__init__(model=_model, query=_manager.get_queryset().query) 
    for key, value in kwargs.items():
        print("has")
        print(f'{key}')
        method_name = f'{key}'
        if hasattr(query, method_name) and value is not None:
            query = getattr(query, method_name)(title__contains="Subscribe to my Odysee")
    query.all()
    print(query.query)
    print(query)
    return query



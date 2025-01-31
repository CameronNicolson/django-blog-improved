from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.conf import settings 

from django.http import Http404

groups = getattr(settings, "EXAMPLE_GROUPS", [])
examples = getattr(settings, "EXAMPLES", [])

def dynamic_template_view(request, *args, **kwargs):
    # Get the last part of the URL and construct the template name
    example_group = kwargs["group_name"]
    example_name = kwargs["example_name"]
    ident = str(example_group + example_name).lower()
    example_data = examples[ident]
    title = example_data["name"]
    template_name = f"{example_name}.html"
    try:
        return render(request, template_name, context={"title": title, **example_data, "breadcrumbs": (("Home", "/"), (f"{example_group}", f"/{example_group}/"),
            (f"{title}", None))})
    except Exception as e:
        raise e

def group_view(request, group_name):
    try:
        group_items = groups[group_name]
    except:
        raise Http404
    title = group_name
    context = { "title": title, 
               "group_items": group_items, 
               "breadcrumbs": (("Home", "/"),(f"{group_name}", None),)}
    return render(request, "group.html", context)

def dummy_view(request, slug=None):
    return HttpResponse(f"You are accessing: {request.path} on the Examples server")

urlpatterns = [
        path("", TemplateView.as_view(template_name="index.html", extra_context={"examples": groups})),
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)),
    re_path(r"^(?P<group_name>[a-z]+)/$", group_view),
    re_path(r"^(?P<group_name>[^/]+)/(?P<example_name>[^/]+)/?$", dynamic_template_view),
    path("<slug:slug>/", dummy_view, name="post_detail"),
]

try: 
    from debug_toolbar.toolbar import debug_toolbar_urls
    print("Debug Toolbar is now enabled in the examples. This gives better insights into the performance and code lifespan.")
    urlpatterns = [
        *debug_toolbar_urls()
    ] + urlpatterns
except:
    pass

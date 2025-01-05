"""
URL configuration for examples.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.conf import settings 

examples = getattr(settings, "EXAMPLES", [])

def dynamic_template_view(request, *args, **kwargs):
    # Get the last part of the URL and construct the template name
    title = kwargs["last_part"]
    template_name = f"{title}.html"
    try:
        return render(request, template_name, context={"title": title})
    except Exception as e:
        raise e

def dummy_view(request, slug=None):
    return HttpResponse(f"You are accessing: {request.path} on the Examples server")

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html", extra_context={"examples": examples})),
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)),
    re_path(r"^.*/(?P<last_part>[^/]+)/?$", dynamic_template_view),
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

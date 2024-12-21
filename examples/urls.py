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
from django.views.generic import TemplateView
from django.http import Http404
from django.shortcuts import render
from django.conf import settings 

examples = getattr(settings, "EXAMPLES", [])

def dynamic_template_view(request, *args, **kwargs):
    # Get the last part of the URL and construct the template name
    template_name = f"{kwargs['last_part']}.html"

    try:
        # Render the template
        return render(request, template_name)
    except Exception:
        # Raise a 404 if the template does not exist
        raise Http404(f"Template '{template_name}' not found.")


urlpatterns = [
        re_path(r"^$", TemplateView.as_view(template_name="index.html", extra_context={"examples": examples})),
    path("admin/", admin.site.urls),
    re_path(r"^.*/(?P<last_part>[^/]+)/?$", dynamic_template_view),
]
"""Default URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from . import views
import debug_toolbar

from blog.sitemaps import PostSitemap

sitemaps = {
    "posts": PostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("cv/", views.cv, name="cv"),
    path("projects/", views.projects, name="projects"),
    path("license/", views.license, name="license"),
    path("services/", views.service, name="services"),
    re_path(r"^([-\w]+)/success/$", views.SuccessFormCreation.as_view(), name="success"),
    path("call-request/", views.CallRequestForm.as_view(), name="call-request"),
    path("", include("blog.urls"), name="blog-urls"),
    path("summernote/", include("django_summernote.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

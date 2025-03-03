from django.urls import include, path


urlpatterns = [
    path("", include("blog_improved.urls"), name="blog-urls"),
]

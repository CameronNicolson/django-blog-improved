from django.urls import include, path
from blog_improved import views 

urlpatterns = [
    path("", include("blog_improved.urls"), name="blog-urls"),
]


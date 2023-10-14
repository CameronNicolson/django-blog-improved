from django.urls import include, path
from django.views.generic.base import TemplateView
from . import views
from .feeds import AtomSiteNewsFeed, LatestPostsFeed

urlpatterns = [
    path("contact/", TemplateView.as_view(template_name="blog_improved/pages/contact.html"), name="contact"),
    path("feed/rss", LatestPostsFeed(), name="rss_feed"),
    path("feed/atom", AtomSiteNewsFeed(), name="atom_feed"),
    path("", views.HomePage.as_view(), name="home"),
    path("all-posts/", views.PostList.as_view(), name="post_list"),
    path("browse/", TemplateView.as_view(template_name="blog_improved/pages/browse.html"), name="browse"),
    path("search/", views.PostList.as_view(), name="search"),
    path("<str:group>/<str:name>", views.AuthorPage.as_view(), name="user_profile"),
    path("<slug:slug>/", views.PostView.as_view(), name="post_detail"),
]

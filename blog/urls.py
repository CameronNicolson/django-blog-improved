from django.urls import include, path

from . import views
from .feeds import AtomSiteNewsFeed, LatestPostsFeed

urlpatterns = [
    path("feed/rss", LatestPostsFeed(), name="rss_feed"),
    path("feed/atom", AtomSiteNewsFeed(), name="atom_feed"),
    path("", views.HomePage.as_view(), name="home"),
    path("index/", views.PostList.as_view(), name="post_list"),
    path("search/", views.PostList.as_view(), name="search"),
    path("<str:group>/<str:name>", views.AuthorPage.as_view(), name="user_profile"),
    path("<slug:slug>/", views.PostView.as_view(), name="post_detail"),
]

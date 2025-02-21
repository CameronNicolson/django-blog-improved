from django.urls import include, path
from django.views.generic.base import TemplateView
from blog_improved import views
from blog_improved.feeds import AtomSiteNewsFeed, LatestPostsFeed

urlpatterns = [
    path("feed/rss", LatestPostsFeed(), name="rss_feed"),
    path("feed/atom", AtomSiteNewsFeed(), name="atom_feed"),
    path("", views.HomePage.as_view(), name="home"),
    path("<str:group>/<str:name>", views.AuthorPage.as_view(), name="user_profile"),
    path("<slug:slug>/", views.PostView.as_view(), name="post_detail"),
]

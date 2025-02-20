from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse

from blog_improved.posts.models import Post

class LatestPostsFeed(Feed):
    title = "My blog"
    link = ""
    description = "Every blog post, sorted by published date."

    def items(self):
        return Post.public.all()

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.created_on

    def item_description(self, item):
        return truncatewords(item.content, 30)
 
from django.utils.feedgenerator import Atom1Feed

class AtomSiteNewsFeed(LatestPostsFeed):
    feed_type = Atom1Feed
    subtitle = LatestPostsFeed.description

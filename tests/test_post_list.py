from blog_improved.posts.posts import PostList 
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.models import Post
from django.test import TestCase

class TestBlogList(TestCase):
    fixtures = ["groups.yaml", "users.yaml", "media.yaml", "tags.yaml", "posts.yaml"]

    def test_create_bloglist(self):
        pl = PostList()
        # PostList is a type of list
        self.assertTrue(isinstance(pl, list))
        posts = Post.objects.all().values_list("id", "title")
        pl_with_param = PostList(posts) 
        ident, title = pl_with_param[0]
        self.assertTrue(isinstance(ident, int))
        self.assertTrue(isinstance(title, str))

    def test_post_list_with_items(self):
        posts = Post.objects.all().values_list("title", "headline", "author__username", "published_on", "content",)
        plist = PostList(posts)
        markup = PostListMarkup("post-list-test", plist, 3, 3, (50,25,25,))
        markup.build_post_list()


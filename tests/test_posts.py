from django.test import TestCase, Client, RequestFactory
from blog.models import Post, User, Tag
from blog.views import PostList
from django.urls import reverse
from django.db import IntegrityError


class TestPosts(TestCase):
    fixtures = ["users.yaml", "media.yaml", "tags.yaml", "posts.yaml"]

    def setup(self):
        pass

    def test_post_list_GET_true(self):
        client = Client()
        response = client.get(reverse("post_list"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "post_list.html")

    def test_redirects_vacant_from_post_list_true(self):
        cleint = Client()
        request = RequestFactory().get("/index/")
        view = PostList()
        view.request = request
        qs = view.get_queryset()
        num_of_posts_in_queryset = qs.count()
        num_of_posts_in_fixtures = 4
        self.assertEquals(num_of_posts_in_queryset, num_of_posts_in_fixtures)

    def test_using_identical_slugs_errors(self):
        author = User.objects.get(pk=1)
        category = Tag.objects.get(pk=1)
        first_post = Post.objects.create(slug="first-post",
        author=author, category=category, title="First post")
        # testing it raises exception 
        with self.assertRaises(IntegrityError):
            Post.objects.create(slug="first-post",
            author=author, category=category, title="Second post")

from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, RequestFactory
from blog.models import Post, User, Tag
from blog.views import PostList
from django.urls import reverse
from django.db import IntegrityError


class TestPosts(TestCase):
    fixtures = ["groups.yaml", "users.yaml", "media.yaml", "tags.yaml", "posts.yaml"]

    def setup(self):
        pass

    def test_post_list_GET_true(self):
        client = Client()
        response = client.get(reverse("post_list"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "post_list.html")

    def test_redirects_vacant_from_post_list_true(self):
        request = RequestFactory().get("/index/")
        view = PostList()
        view.request = request
        qs = view.get_queryset()
        num_of_posts_in_queryset = qs.count()
        num_expected_posts_in_fixtures = 5
        self.assertEquals(num_of_posts_in_queryset, num_expected_posts_in_fixtures)

    def test_post_identical_slug_errors(self):
        # testing it raises exception 
        with self.assertRaises(IntegrityError) as raised:
            Post.objects.create(slug="listen-to-your-customers",
            author=User.objects.get(pk=1), category=Tag.objects.get(pk=1))
            self.assertEquals(
                "UNIQUE constraint failed",
                str(raised.exception)
            )

    def test_get_404_viewing_draft(self):
        client = Client()
        slug = Post.objects.get(pk=6).slug
        response = client.get(reverse("post_detail", kwargs={"slug": slug}))
        self.assertEquals(
            response.status_code, 
            404
        )
        self.assertTemplateUsed(
            response, 
            "404.html"
        )

    def test_basic_user_create_post_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.add_post')
        self.assertEquals(
            has_perm, 
            False
        )

    def test_basic_user_edit_post_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.change_post')
        self.assertEquals(
            has_perm, 
            False
        )

    def test_basic_user_delete_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.delete_post')
        self.assertEquals(
            has_perm, 
            False
        )

    def test_basic_user_view_permissions_denied(self):
        # realise that basic users are denied from viewing
        # since some posts are considered private,
        # or not ready for the public sphere
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.view_post')
        self.assertEquals(
            has_perm, 
            False
        )

    def test_author_url_active(self):
        post = Post.objects.get(slug="this-post-is-featured")
        journalist = get_user_model().objects.get(username="journalist")
        self.assertEquals(
            post.author,
            journalist
        )
        
        self.assertEquals(
            post.get_author_url(), 
            "/author/journalist" 
        )

    def test_author_url_missing(self):
        post = Post.objects.get(slug="15-tips-for-mission-success")
        alice = get_user_model().objects.get(username="alice")
        self.assertEquals(
            post.author,
            alice
        )
        
        self.assertEquals(
            post.get_author_url(), 
            None
        )

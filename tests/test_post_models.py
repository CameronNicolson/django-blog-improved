from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, RequestFactory
from blog_improved.posts.models import Post, User, Tag
from django.urls import reverse
from django.db import IntegrityError
from pathlib import Path
import yaml

DATA_DIR = Path.cwd() / "tests" / "fixtures"

class TestPosts(TestCase):
    fixtures = ["groups.yaml", "users.yaml", "media.yaml", "tags.yaml", "posts.yaml"]
    num_of_entries = []
    post_public_count = 0
    post_private_count = 0
    post_unlisted_count = 0
    post_draft_count = 0
    post_redirect_count = 0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
        for file_name in cls.fixtures:
            file_path = Path(DATA_DIR / file_name)
            total_entries = cls.count_yaml_entries(file_path)
            cls.num_of_entries.append(total_entries)
            if file_path.name == "posts.yaml":
                statuses = cls.count_num_of_statuses(file_path)
                cls.post_draft_count, cls.post_public_count, cls.post_private_count, cls.post_unlisted_count, cls.post_redirect_count = statuses 

    def count_yaml_entries(file_path):
        with open(file_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
  
        num_entries = len(yaml_data)
        return num_entries

    def count_num_of_statuses(file_path):
        with open(file_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
       
        post_draft = 0
        post_public = 0
        post_private = 0 
        post_unlisted = 0
        post_redirect = 0
        for post in yaml_data:
            try:
                if post["model"] == "blog_improved.postshoutout":
                    post_redirect += 1
                elif post["model"] != "blog_improved.post":
                    continue
                if post["fields"]["status"] == 0:
                    post_draft += 1
                elif post["fields"]["status"] == 1:
                    post_public += 1
                elif post["fields"]["status"] == 2:
                    post_private += 1
                elif post["fields"]["status"] == 3:
                    post_unlisted += 1
            except KeyError:
                print("no status field")
                print(post["fields"])
        return (post_draft, post_public, post_private, post_unlisted, post_redirect,)

    def test_post_identical_slug_errors(self):
        # testing it raises exception 
        with self.assertRaises(IntegrityError) as raised:
            Post.objects.create(slug="listen-to-your-customers",
            author=User.objects.get(pk=1), category=Tag.objects.get(pk=1))
            self.assertEqual(
                "UNIQUE constraint failed",
                str(raised.exception)
            )

    def test_get_404_viewing_draft(self):
        client = Client()
        slug = Post.objects.get(pk=6).slug
        response = client.get(reverse("post_detail", kwargs={"slug": slug}))
        self.assertEqual(
            response.status_code, 
            404
        )

    def test_basic_user_create_post_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.add_post')
        self.assertEqual(
            has_perm, 
            False
        )

    def test_basic_user_edit_post_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.change_post')
        self.assertEqual(
            has_perm, 
            False
        )

    def test_basic_user_delete_permissions_denied(self):
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.delete_post')
        self.assertEqual(
            has_perm, 
            False
        )

    def test_basic_user_view_permissions_denied(self):
        # realise that basic users are denied from viewing
        # since some posts are considered private,
        # or not ready for the public sphere
        basic_user = User.objects.get(username="basic")
        has_perm = basic_user.has_perm('blog.view_post')
        self.assertEqual(
            has_perm, 
            False
        )

    def test_author_url_active(self):
        post = Post.objects.get(slug="this-post-is-featured")
        journalist = get_user_model().objects.get(username="journalist")
        self.assertEqual(
            post.author,
            journalist
        )
        
        self.assertEqual(
            post.get_author_url(), 
            "/author/journalist/" 
        )
    
    def test_author_url_missing(self):
        post = Post.objects.get(slug="15-tips-for-mission-success")
        alice = get_user_model().objects.get(username="alice")
        self.assertEqual(
            post.author,
            alice
        )
        
        self.assertEqual(
            post.get_author_url(), 
            None
        )

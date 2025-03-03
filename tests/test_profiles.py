from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.test import TestCase, Client
from blog_improved.models import BlogGroup
from blog_improved.authors.models import UserProfile
from django.urls import reverse
from django.test.utils import override_settings
from django.conf import settings
from blog_improved.models import Status

class TestProfiles(TestCase):
    fixtures = ["groups.yaml", "users.yaml",]

    def setup(self):
        pass

    def test_status_code_choice(self):
        from blog_improved.authors.models import user_profile_choice_code
        code = user_profile_choice_code(False)
        self.assertEqual(
                code, 
                2
        )
        code = user_profile_choice_code(True)
        self.assertEqual(
                code, 
                1
        )

    def test_new_userprofile_status_public_status(self):
        from blog_improved.conf import USER_PUBLIC_PROFILE
        self.assertEqual(
                USER_PUBLIC_PROFILE,
                True
        )
        user = User.objects.create(
                username="snowden",
                password="password123",
        )
        user.save()
        group = BlogGroup.objects.get(name="author")
        group.user_set.add(user)

        # User was added to group
        self.assertTrue(user.groups.filter(name="author").exists())

        UserProfile.objects.create(user=user)
        profile = UserProfile.objects.get(user=user)
        # status code *1* represents public
        self.assertEqual(profile.status, 1)
        client = Client()
        self.assertEqual(group.name, "author")
        self.assertEqual(user.username, "snowden")
        response = client.get(reverse("user_profile", kwargs={"group": group.name, "name": user.username}))
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertTemplateUsed(
            response,
            "blog_improved/pages/author.html"
        )

    def test_nonstaffer_userprofile_change_denied(self):
        # our resident basic account 
        non_staffer = get_user_model().objects.get(username="basic")
        app_label = apps.get_app_config('blog_improved').verbose_name.lower()
        self.assertEqual(
            app_label,
            "blog_improved"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEqual(
            model_name,
            "userprofile"
        ) 
        self.assertEqual(
            non_staffer.is_superuser,
            False
        )
        self.assertEqual(
            non_staffer.is_staff,
            False
        )

        self.assertEqual(
            non_staffer.has_perm(f"{app_label}.change_{model_name}"),
            False
        )

    def test_nonstaffer_userprofile_view_denied(self):
        # our resident basic account 
        non_staffer = get_user_model().objects.get(username="basic")
        app_label = apps.get_app_config('blog_improved').verbose_name.lower()
        self.assertEqual(
            app_label,
            "blog_improved"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEqual(
            model_name,
            "userprofile"
        ) 
        self.assertEqual(
            non_staffer.is_superuser,
            False
        )
        self.assertEqual(
            non_staffer.is_staff,
            False
        )
        self.assertEqual(
            non_staffer.has_perm(f"{app_label}.view_{model_name}"),
            False
        )

    def test_superuser_can_change_userprofile(self):
         # our resident superuser alice 
        superuser = get_user_model().objects.get(username="alice")
        app_label = apps.get_app_config("blog_improved").verbose_name.lower()
        self.assertEqual(
            app_label,
            "blog_improved"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEqual(
            model_name,
            "userprofile"
        ) 
        self.assertEqual(
            superuser.is_superuser,
            True
        ) 
        self.assertEqual(
            superuser.has_perm(f"{app_label}.change_{model_name}"),
            True
        )

    def test_authorpage_multiple_authors_200(self):
        basic = get_user_model().objects.get(username="basic")
        journalist = get_user_model().objects.get(username="journalist")
        author_group, created = BlogGroup.objects.get_or_create(name="author")
        author_group.status = Status.PUBLISH.value
        author_group.save()
        author_group.user_set.add(basic)
        author_group.user_set.add(journalist)
        UserProfile.objects.create(user=basic, status=1)
        UserProfile.objects.create(user=journalist, status=1)
        self.assertEqual(UserProfile.objects.get(user=basic).status, 
                         Status.PUBLISH.value)

        self.assertEqual(UserProfile.objects.get(user=journalist).status,
                         Status.PUBLISH.value)

        client = Client()
        response = client.get(reverse("user_profile", kwargs={"group": author_group.name, "name": f"{basic.username},{journalist.username}"}))
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertTemplateUsed(
            response,
            "blog_improved/pages/author.html"
        )


    def test_authorpage_multiple_authors_404(self):
        basic = get_user_model().objects.get(username="basic")
        journalist = get_user_model().objects.get(username="journalist")
        author_group, created = BlogGroup.objects.get_or_create(name="author")
        author_group.user_set.add(basic)
        author_group.user_set.add(journalist)
        journalist_profile = UserProfile.objects.create(user=journalist)
        journalist_profile.status = 2
        journalist_profile.save()
        self.assertEqual(
                UserProfile.objects.get(user=journalist).status,
                2
        )
        client = Client()
        response = client.get(reverse("user_profile", kwargs={"group": author_group.name, "name": f"{basic.username},{journalist.username}"}))
        self.assertEqual(
            response.status_code,
            404
        )


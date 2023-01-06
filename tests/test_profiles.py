from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from blog.models import User, UserProfile
from django.urls import reverse

class TestProfiles(TestCase):
    fixtures = ["users.yaml",]

    def setup(self):
        pass

    def test_new_userprofile_status_private_status(self):
        user = User.objects.create(
                username="snowden",
                password="password123"
        )
        user.save()
        profile = UserProfile.objects.get(user=user)
        # status code *2* represents private
        self.assertEquals(profile.status, 2)

        client = Client()
        response = client.get(reverse("author", kwargs={"name": user.username}))
        self.assertEquals(
            response.status_code,
            404
        )
        self.assertTemplateUsed(
            response,
            "404.html"
        )

    def test_nonstaffer_userprofile_change_denied(self):
        # our resident basic account 
        non_staffer = get_user_model().objects.get(username="basic")
        app_label = apps.get_app_config('blog').verbose_name.lower()
        self.assertEquals(
            app_label,
            "blog"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEquals(
            model_name,
            "userprofile"
        ) 
        self.assertEquals(
            non_staffer.is_superuser,
            False
        )
        self.assertEquals(
            non_staffer.is_staff,
            False
        )

        self.assertEquals(
            non_staffer.has_perm(f"{app_label}.change_{model_name}"),
            False
        )

    def test_nonstaffer_userprofile_view_denied(self):
        # our resident basic account 
        non_staffer = get_user_model().objects.get(username="basic")
        app_label = apps.get_app_config('blog').verbose_name.lower()
        self.assertEquals(
            app_label,
            "blog"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEquals(
            model_name,
            "userprofile"
        ) 
        self.assertEquals(
            non_staffer.is_superuser,
            False
        )
        self.assertEquals(
            non_staffer.is_staff,
            False
        )
        self.assertEquals(
            non_staffer.has_perm(f"{app_label}.view_{model_name}"),
            False
        )

    def test_superuser_can_change_userprofile(self):
         # our resident superuser alice 
        superuser = get_user_model().objects.get(username="alice")
        app_label = apps.get_app_config('blog').verbose_name.lower()
        self.assertEquals(
            app_label,
            "blog"
        )
        model_name = UserProfile.__name__.lower()
        self.assertEquals(
            model_name,
            "userprofile"
        ) 
        self.assertEquals(
            superuser.is_superuser,
            True
        ) 
        self.assertEquals(
            superuser.has_perm(f"{app_label}.change_{model_name}"),
            True
        )

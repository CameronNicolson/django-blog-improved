from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.test import TestCase, Client
from blog.models import BlogGroup, User, UserProfile
from django.urls import reverse
from django.test.utils import override_settings
from django.conf import settings

class TestProfiles(TestCase):
    fixtures = ["groups.yaml", "users.yaml",]

    def setup(self):
        pass

    def test_status_code_choice(self):
        from blog.models import user_profile_choice_code
        code = user_profile_choice_code(False)
        self.assertEquals(
                code, 
                2
        )
        code = user_profile_choice_code(True)
        self.assertEquals(
                code, 
                1
        )

    def test_new_userprofile_status_public_status(self):
        from blog.conf import USER_PUBLIC_PROFILE
        self.assertEquals(
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
        profile = UserProfile.objects.get(user=user)
        # status code *1* represents public
        self.assertEquals(profile.status, 1)
        client = Client()
        response = client.get(reverse("author", kwargs={"group": group.name, "name": user.username}))
        self.assertEquals(
            response.status_code,
            200
        )
        self.assertTemplateUsed(
            response,
            "pages/author.html"
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

    def test_authorpage_multiple_authors_200(self):
        basic = get_user_model().objects.get(username="basic")
        journalist = get_user_model().objects.get(username="journalist")
        author_group, created = BlogGroup.objects.get_or_create(name="author")
        author_group.user_set.add(basic)
        author_group.user_set.add(journalist)
        
        client = Client()
        response = client.get(reverse("author", kwargs={"group": author_group.name, "name": f"{basic.username},{journalist.username}"}))
        self.assertEquals(
            response.status_code,
            200
        )
        self.assertTemplateUsed(
            response,
            "pages/author.html"
        )


    def test_authorpage_multiple_authors_404(self):
        basic = get_user_model().objects.get(username="basic")
        journalist = get_user_model().objects.get(username="journalist")
        author_group, created = BlogGroup.objects.get_or_create(name="author")
        author_group.user_set.add(basic)
        author_group.user_set.add(journalist)
        journalist_profile = UserProfile.objects.get(user=journalist)
        journalist_profile.status = 2
        journalist_profile.save()
        self.assertEquals(
                UserProfile.objects.get(user=journalist).status,
                2
        )
        client = Client()
        response = client.get(reverse("author", kwargs={"group": author_group.name, "name": f"{basic.username},{journalist.username}"}))
        self.assertEquals(
            response.status_code,
            404
        )
        self.assertTemplateUsed(
            response,
            "404.html"
        )

    def test_user_profile_default_absolute_url(self):
        journalist = get_user_model().objects.get(username="journalist")
        profile = UserProfile.objects.get(user=journalist)
        client = Client()
        req = self.client.get('/')

        profile_url = profile.get_absolute_url(req, groupname="author")
        expected_url = f"{get_current_site(req)}/author/{journalist.username}"
        self.assertEquals(
            profile_url, 
            expected_url
        )

    def test_user_profile_custom_absolute_url(self):
        journalist = get_user_model().objects.get(username="journalist")
        profile = UserProfile.objects.get(user=journalist)
        # add website to profile
        custom_url = "https://socialmedia.local"
        profile.website = custom_url
        profile.save()
        client = Client()
        req = self.client.get('/')
        profile_url = profile.get_absolute_url(req, groupname="author")
        expected_url = custom_url
        self.assertEquals(
            profile_url, 
            expected_url
        )

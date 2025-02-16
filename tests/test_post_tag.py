import io
from django.urls import path, reverse
from django.views.generic import TemplateView
from datetime import datetime, timezone
from classytags.exceptions import TooManyArguments
from pathlib import Path
from django.test import TestCase, override_settings
from bs4 import BeautifulSoup
from django.template import Context, Template, TemplateSyntaxError
from blog_improved.posts.models import Post
from django.template import engines

urlpatterns = []

TEST_TEMPLATES = {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],  # No actual directory needed
    "APP_DIRS": False,  # Disable automatic file-based templates
    "OPTIONS": {
        "loaders": [("django.template.loaders.locmem.Loader", {
            "single_post.html": """
            {% load blog_tags %}
            <!DOCTYPE html>
            <html>
            <head><title>{{ title }}</title></head>
            <body>
                {% post %}
            </body>
            </html>
            """
        })]
    },
}

class PostTagTestCase(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]
    
    def load_fixture(self, filename):
        file = Path.cwd() / "tests" / "fixtures" / "html" / filename
        with open(file, "r") as f:
            return f.read()
       
    def test_post_tag_missing_post(self):
        template_string = '{% load blog_tags %}{% post %}'
        template = Template(template_string)
        context = Context({"post": {"slug": "bad-request"}})
        with self.assertRaises(TemplateSyntaxError):
            rendered_html = template.render(context)

    def test_post_tag_empty_slug(self):
        template_string = '{% load blog_tags %}{% post %}'
        template = Template(template_string)
        context = Context({"post": {"slug": ""}})
        with self.assertRaises(TemplateSyntaxError):
            rendered_html = template.render(context)

    def test_post_tag_no_args(self):
        expected_html = self.load_fixture("single_post_valid.html") 
        template_string = '{% load blog_tags %}{% post %}'
        template = Template(template_string)
        context = Context({"post": {"slug": "sleep"}})
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, "html.parser") 
        rendered_expected = BeautifulSoup(expected_html, "html.parser")
        rendered_article = rendered.find(class_="article")
        article_exists = True if rendered_article else False
        self.assertTrue(article_exists)
        rendered_title = rendered_article.find(class_="article__title")
        expected_title = rendered_expected.find(class_="article__title") 
        rendered_title_text = rendered_title.text
        expected_title_text = expected_title.text
        self.assertEqual(rendered_title_text, expected_title_text)
        rendered_date = rendered_expected.find(class_="article__time--published-date")
        article_datetime = datetime.fromisoformat(rendered_date.attrs["datetime"])  
        expected_datetime = datetime(day=4, month=8, year=2023, 
                                     hour=11, minute=22, second=33, microsecond=444555, tzinfo=timezone.utc)
        self.assertEqual(article_datetime, expected_datetime)
        rendered_author = rendered.find(class_="article__author")
        expected_author = rendered_expected.find(class_="article__author")
        try:
            article_author_text = rendered_author.text  
            expected_author_text = expected_author.text
        except:
            article_author_text = False
            expected_author_text = False

        self.assertEqual(article_author_text, expected_author_text) 
        rendered_content = rendered.find(class_="article__content")
        expected_author = rendered_expected.find(class_="article__content") 
        self.assertTrue(rendered_content)

    def test_post_tag_id_only_arg(self):
        template_string = '{% load blog_tags %}{% post id=14 %}'
        template = Template(template_string)
        context = Context({}) 
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, "html.parser") 

        rendered_article_exists = rendered.find(class_="article")
        self.assertTrue(rendered_article_exists)
        self.assertTrue(bool(rendered.find(class_="article__title")))
        self.assertTrue(bool(rendered.find(class_="article__author")))
        self.assertTrue(bool(rendered.find(class_="article__category")))
        self.assertTrue(bool(rendered.find(class_="article__time--published-date")))

    def test_post_tag_no_id_or_slug(self):
        template_string = '{% load blog_tags %}{% post %}'
        template = Template(template_string)
        context = Context({}) 
        with self.assertRaisesRegex(
            TemplateSyntaxError,
            r"Neither id nor slug was provided\."
        ):
            rendered_html = template.render(context) 

    def test_post_tag_invalid_id(self):
        template_string = '{% load blog_tags %}{% post id=999999999 %}'
        template = Template(template_string)
        context = Context({}) 
        with self.assertRaisesRegex(
            TemplateSyntaxError,
            r"No matching records found"
        ):
            rendered_html = template.render(context) 

    def test_post_tag_multiple_id_args(self):
        template_string = '{% load blog_tags %}{% post id="12" 22 hi %}'
        with self.assertRaises(TooManyArguments):
            template = Template(template_string)
 
    def test_post_tag_multiple_template_calls(self):
        post_tags = ["post id=22", "post id=23", "post id=17"]
        template_string = "{% load blog_tags %}"
        template_string = template_string + " ".join( "{% " + tag + " %} " for tag in post_tags)
        template = Template(template_string)
        context = Context({})  
        rendered_html = template.render(context) 
        rendered = BeautifulSoup(rendered_html, "html.parser") 
        article_elements = rendered.find_all(class_="article")
        expected_total_articles = len(post_tags)
        total_articles = len(article_elements)
        self.assertEqual(total_articles, expected_total_articles)
        prev_title = []
        # Checks all titles were unique 
        for n, elem in enumerate(article_elements):
            # Find title
            title = elem.find(class_="article__title")
            self.assertTrue(bool(title))
            self.assertEqual(len(prev_title), n)
            self.assertFalse(title.text in prev_title)
            prev_title.append(title.text)


    @override_settings(ROOT_URLCONF=__name__, TEMPLATES=[TEST_TEMPLATES])
    def test_post_tag_prefetch_valid(self):
        from django.urls import path
        from django.views.generic import TemplateView

        hot_dog_posts = Post.objects.filter(title__icontains="hot dog").order_by("-published_on")
        self.assertEqual(len(hot_dog_posts), 2)
        newest_post = hot_dog_posts.first()
        actual_post_year = newest_post.published_on.year
        expected_post_year = 2025
        self.assertEqual(actual_post_year, expected_post_year)
        urlpatterns.append(path("hot-dog-competition/",
                        TemplateView.as_view(
                        template_name="single_post.html",
                        extra_context={"post": newest_post, 
                                       "title": "hot dog comp"},
                    ),
                    name="hot_dog_event"
                )
        )

        response = self.client.get(reverse("hot_dog_event"))
        self.assertEqual(response.status_code, 200) 
        rendered_html = response.rendered_content
        rendered = BeautifulSoup(rendered_html, "html.parser") 
        expected_heading = "Hot Dog Competition 2025"
        actual_heading = rendered.find(class_="article__title").text
        self.assertEqual(actual_heading, expected_heading)
        actual_author = rendered.find(class_="article__author").text
        expected_author = "alice"
        self.assertEqual(actual_author, expected_author)

    def test_post_tag_missing_author(self):
        context_missing_author = {"post": {"title": "Anonymous", "headline": "We are legion"}} 
        template_string = '{% load blog_tags %}{% post %}'
        template = Template(template_string)
        context = Context(context_missing_author)
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, "html.parser") 
        actual_author = rendered.find(class_="article__author")
        self.assertTrue(actual_author == None)

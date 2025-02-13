import io
from datetime import datetime, timezone
from classytags.exceptions import TooManyArguments
from pathlib import Path
from django.test import TestCase
from bs4 import BeautifulSoup
from django.template import Context, Template, TemplateSyntaxError

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
        template_string = '{% load blog_tags %}{% post 14 %}'
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
        template_string = '{% load blog_tags %}{% post 999999999 %}'
        template = Template(template_string)
        context = Context({}) 
        with self.assertRaisesRegex(
            TemplateSyntaxError,
            r"No matching records found"
        ):
            rendered_html = template.render(context) 

    def test_post_tag_multiple_id_args(self):
        template_string = '{% load blog_tags %}{% post 12 22 hi %}'
        with self.assertRaises(TooManyArguments):
            template = Template(template_string)
 

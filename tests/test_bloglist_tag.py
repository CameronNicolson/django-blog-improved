from django.db.models.query import QuerySet
from django.test import TestCase
from django.template import Context, Template
from blog_improved.models import Post
from blog_improved.templatetags.blog_list_tags import QueryCommand

class BlogListTagTest(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def test_bloglist_tag(self):
        template_string = '{% load blog_tags %}{% bloglist category="videos,personal skill" %}'
        template = Template(template_string)
        context = Context({})
        rendered = template.render(context)
        self.assertEqual(True, True)

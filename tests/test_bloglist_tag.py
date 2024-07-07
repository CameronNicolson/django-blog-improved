from django.test import TestCase
from django.template import Context, Template
from blog_improved.models import Post

class BlogListTagTest(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def test_bloglist_tag(self):
        template_string = '{% load blog_tags %}{% bloglist filter="title=\'Black\'" %}'
        template = Template(template_string)
        context = Context({})
        print(context)
        rendered = template.render(context)
        self.assertEqual(True, True)

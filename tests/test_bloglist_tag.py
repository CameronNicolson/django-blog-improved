from django.test import TestCase
from django.template import Context, Template

class BlogListTagTest(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def test_bloglist_tag(self):
        template_string = '{% load blog_tags %}{% bloglist category=5 %}'
        template = Template(template_string)
        context = Context({})
        rendered = template.render(context)
        self.assertEqual(rendered, "{}")

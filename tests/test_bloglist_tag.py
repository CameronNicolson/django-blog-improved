from django.test import TestCase
from django.template import Context, Template

class BlogListTagTest(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def test_bloglist_tag_no_args(self):
        template_string = '{% load blog_tags %}{% bloglist %}'
        template = Template(template_string)
        context = Context({})
        rendered = template.render(context)
        self.assertEqual(len(rendered), 943)

    def test_bloglist_tag(self):
        template_string = '{% load blog_tags %}{% bloglist max_count="22" category="colors,programming" %}'
        template = Template(template_string)
        context = Context({})
        rendered = template.render(context)
        self.assertEqual(rendered, "<ul><li>The color red facts</li><li>The color yellow facts</li><li>My coding project</li><li>Working title</li></ul>")

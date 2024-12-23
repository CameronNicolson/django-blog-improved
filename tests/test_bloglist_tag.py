import io
from pathlib import Path
from django.test import TestCase
from bs4 import BeautifulSoup
from django.template import Context, Template

class BlogListTagTestCase(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def load_fixture(self, filename):
        file = Path.cwd() / "tests" / "fixtures" / "html" / filename
        with open(file, "r") as f:
            return f.read()
    
    @staticmethod
    def count_siblings(parent):
        count = 0
        for child in parent:
            count = count + 1
        return count

    @staticmethod
    def count_post_items(parent):
        count = len(parent.findAll(class_="posts__item"))
        return count
    
    def test_bloglist_tag_no_args(self):
        template_string = '{% load blog_tags %}{% bloglist %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        rendered_list = rendered.find(id="bloglist")
        bloglist_exists = True if rendered_list else False
        self.assertTrue(bloglist_exists)
        bloglist_item_count = len(rendered_list.find_all(class_="posts__item"))
        self.assertEqual(bloglist_item_count, 9)


    def test_bloglisttag_invalid_negative_max_count(self):
        template_string = '{% load blog_tags %}{% bloglist max_count="-1" %}'
        template = Template(template_string)
        context = Context({})
        render = template.render(context) 

    def test_bloglisttag_multiple_categories(self):
        expected_html = self.load_fixture("bloglist_multiple_categories.html") 
        template_string = '{% load blog_tags %}{% bloglist max_count="22" category="colors,programming" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        expected_list = expected.find(id="bloglist")
        rendered_list = rendered.find(id="bloglist")

        self.assertTrue(expected_list is not None)
        self.assertTrue(rendered_list is not None)
        # Count the number of <li> elements within the <ul>
        expected_post_count = BlogListTagTestCase.count_post_items(expected_list)
        rendered_post_count = BlogListTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_post_count, expected_post_count)
        expected_categories = expected_list.find_all("a", attrs={"rel": "category"})
        rendered_categories = rendered_list.find_all("a", attrs={"rel": "category"})
        expected_categories_count = len(expected_categories)        
        rendered_categories_count = len(rendered_categories)
        self.assertEqual(rendered_categories_count, expected_categories_count)
        for expected_cat, rendered_cat in zip(expected_categories, rendered_categories):
            self.assertTrue(expected_cat.text in ["colors","programming"])
            self.assertTrue(rendered_cat.text in ["colors","programming"])

    def test_bloglisttag_featured(self):
        expected_html = self.load_fixture("bloglist_featured.html")
        template_string = '{% load blog_tags %}{% bloglist name="featured-news" featured="True" max_count="1" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        
        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser')
        expected_list = expected.find(id="featured-news")
        rendered_list = rendered.find(id="featured-news")
        self.assertTrue(rendered_list is not None)

        expected_post = expected_list.find(class_="posts__item")
        rendered_post = rendered_list.find(class_="posts__item")

        self.assertTrue(expected_post is not None)
        self.assertTrue(rendered_post is not None)

        # Check the article content
        expected_article = expected_post.find("article")
        rendered_article = rendered_post.find("article")
        self.assertTrue(rendered_article is not None)

        self.assertTrue("article--featured" in expected_article.attrs["class"])
        self.assertTrue("article--featured" in rendered_article.attrs["class"])
        # Check h1, h2, and address content
        self.assertEqual(rendered_article.find('h1').text, expected_article.find('h1').text)
        self.assertEqual(rendered_article.find('h2').text, expected_article.find('h2').text)
        expected_author = expected_article.find('address').find('a')
        rendered_author = rendered_article.find('address').find('a')
        self.assertEqual(rendered_author.text, expected_author.text)
        self.assertEqual(rendered_author['href'], expected_author['href'])

    def test_bloglisttag_featured_and_ordinary_posts(self):
        expected_html = self.load_fixture("bloglist_mix_feature_ordinary_posts.html")
        template_string = '{% load blog_tags %}{% bloglist name="latest-news" featured="True" featured_count="2" max_count="5" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        
        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser')

        # Check the `ul` element with id `latest-news__list`
        expected_list = expected.find(id="latest-news")
        rendered_list = rendered.find(id="latest-news")

        self.assertTrue(expected_list is not None)
        self.assertTrue(rendered_list is not None)
        expected_post_count = BlogListTagTestCase.count_post_items(expected_list)

        rendered_post_count = BlogListTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_post_count, 5) 

        rendered_featured_count = len(rendered_list.find_all("article", attrs={"class": "article--featured"}))

        self.assertEqual(rendered_featured_count, 2) 


    def test_bloglisttag_featured_and_feature_count(self):
        template_string = '{% load blog_tags %}{% bloglist name="latest-news" featured="True" featured_count="2" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)

        # Parse both HTML strings
        rendered = BeautifulSoup(rendered_html, 'html.parser')
        # Check the `ul` element with id `latest-news__list`
        rendered_list = rendered.find(id="latest-news")

        self.assertTrue(rendered_list is not None)
        rendered_posts_count = BlogListTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_posts_count, 9) 
        rendered_featured_count = len(rendered_list.find_all("article", attrs={"class": "article--featured"}))

        self.assertEqual(rendered_featured_count, 2) 

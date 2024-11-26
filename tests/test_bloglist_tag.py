from django.test import TestCase
from bs4 import BeautifulSoup
from django.template import Context, Template

class BlogListTagTest(TestCase):
    fixtures = ["media.yaml", "tags.yaml", "users.yaml", "redirects.yaml", "groups.yaml", "posts.yaml"]

    def test_bloglist_tag_no_args(self):
        template_string = '{% load blog_tags %}{% bloglist %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        rendered_ul = rendered.find("ul", attrs={"id": "bloglist__list"})
        ul_exists = True if rendered_ul else False
        self.assertTrue(ul_exists)

    def test_bloglisttag_multiple_categories(self):
        expected_html = '''
<div class="container"><ul id="bloglist__list"><li class="bloglist__list-item col-one-third"><article class="article"><h1 class="article__title">The color red facts</h1><address class="article__author"><a rel="basic" href="/author/basic" class="article__author-link">basic</a></address><time class="article__time--published-date" datetime="2024-01-12T11:03:10+00:00">12 January 2024</time><a rel="category" class="author__category--link" href="#">colors</a></article></li><li class="bloglist__list-item col-one-third"><article class="article"><h1 class="article__title">The color yellow facts</h1><h2 class="article__headline">Yellow represents</h2><address class="article__author"><a rel="basic" href="/author/basic" class="article__author-link">basic</a></address><time class="article__time--published-date" datetime="2024-01-11T10:10:10+00:00">11 January 2024</time><a rel="category" class="author__category--link" href="#">colors</a></article></li><li class="bloglist__list-item col-one-third"><article class="article"><h1 class="article__title">My coding project</h1><address class="article__author"><a rel="alice" href="/author/alice" class="article__author-link">alice</a></address><time class="article__time--published-date" datetime="2022-06-02T13:52:00+00:00">02 June 2022</time><a rel="category" class="author__category--link" href="#">programming</a></article></li></ul></div>
'''
  
        template_string = '{% load blog_tags %}{% bloglist max_count="22" category="colors,programming" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        expected_ul = expected.find("ul", {"id": "bloglist__list"})
        rendered_ul = rendered.find('ul', {'id': 'bloglist__list'})
        self.assertTrue(rendered_ul is not None)
        # Count the number of <li> elements within the <ul>
        expected_li_count = len(expected_ul.find_all("li"))
        rendered_li_count = len(rendered_ul.find_all("li"))
        self.assertEqual(rendered_li_count, expected_li_count)
        expected_categories = expected_ul.find_all("a", attrs={"rel": "category"})
        rendered_categories = rendered_ul.find_all("a", attrs={"rel": "category"})
        expected_categories_count = len(expected_categories)        
        rendered_categories_count = len(rendered_categories)
        self.assertEqual(rendered_categories_count, expected_categories_count)
        for expected_cat, rendered_cat in zip(expected_categories, rendered_categories):
            self.assertTrue(expected_cat.text in ["colors","programming"])
            self.assertTrue(rendered_cat.text in ["colors","programming"])

    def test_bloglisttag_featured(self):
        expected_html = '''
        <div class="container"><ul id="featured-news__list"><li class="featured-news__list-item col-one-third"><article><h1>Welcome to my blog</h1><h2>An audience with the internet</h2><address class="author"><a rel="journalist" href="/author/journalist" class="author__link">journalist</a></address></article></li></ul></div>
        '''
        template_string = '{% load blog_tags %}{% bloglist name="featured-news" featured="True" max_count="1" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)

        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser')
        # Check the `ul` element with id `bob__list`
        expected_ul = expected.find('ul', {'id': 'featured-news__list'})
        rendered_ul = rendered.find('ul', {'id': 'featured-news__list'})
        self.assertTrue(rendered_ul is not None)

        # Check the `li` element with class `bob__list-item`
        expected_li = expected_ul.find('li', {'class': 'featured-news__list-item'})
        rendered_li = rendered_ul.find('li', {'class': 'featured-news__list-item'})
        self.assertTrue(rendered_li is not None)

        # Check the article content
        expected_article = expected_li.find('article')
        rendered_article = rendered_li.find('article')
        self.assertTrue(rendered_article is not None)
    
        # Check h1, h2, and address content
        self.assertEqual(rendered_article.find('h1').text, expected_article.find('h1').text)
        self.assertEqual(rendered_article.find('h2').text, expected_article.find('h2').text)
        expected_author = expected_article.find('address').find('a')
        rendered_author = rendered_article.find('address').find('a')
        self.assertEqual(rendered_author.text, expected_author.text)
        self.assertEqual(rendered_author['href'], expected_author['href'])

 

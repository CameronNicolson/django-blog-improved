import io
from pathlib import Path
from django.test import TestCase
from bs4 import BeautifulSoup
from django.template import Context, Template, TemplateSyntaxError

class PostlistTagTestCase(TestCase):
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
    
    def test_postlist_tag_no_args(self):
        template_string = '{% load blog_tags %}{% postlist %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        rendered_list = rendered.find(id="postlist")
        postlist_exists = True if rendered_list else False
        self.assertTrue(postlist_exists)
        postlist_item_count = len(rendered_list.find_all(class_="posts__item"))
        self.assertEqual(postlist_item_count, 9)

    def test_postlisttag_default_order(self):
        # order should be time newest to oldest
        template_string = "{% load blog_tags %}{% postlist %}"
        template = Template(template_string)
        context = Context({})
        render = template.render(context) 
        rendered = BeautifulSoup(render, 'html.parser') 
        rendered_list = rendered.find(id="postlist")
        self.assertTrue(rendered_list is not None)
        all_post_times = rendered_list.findAll(class_="article__time--published-date")
        original_publish_dates = [time["datetime"] for time in all_post_times]
        sorted_publish_dates  = sorted(original_publish_dates, reverse=True)
        # test lists are in the same order
        self.assertEqual(original_publish_dates, 
                         sorted_publish_dates)



    def test_postlisttag_invalid_negative_max_count(self):
        template_string = '{% load blog_tags %}{% postlist max_count="-1" %}'
        template = Template(template_string)
        context = Context({})
        render = template.render(context) 
        rendered = BeautifulSoup(render, 'html.parser') 
        rendered_list = rendered.find(id="postlist")
        self.assertTrue(rendered_list is not None)

    def test_postlisttag_empty_max_count(self):
        template_string = '{% load blog_tags %}{% postlist max_count="" %}'
        template = Template(template_string)
        context = Context({})
        render = template.render(context) 
        rendered = BeautifulSoup(render, 'html.parser') 
        rendered_list = rendered.find(id="postlist")
        self.assertTrue(rendered_list is not None)
        # Count the number of <li> elements within the <ul>
        expected_post_count = PostlistTagTestCase.count_post_items(rendered_list)
        print(rendered_list)
        self.assertEqual(expected_post_count, 9)
 
    def test_postlisttag_undefined_layout(self):
        bad_layout = "bad"
        template_string = "{% load blog_tags %}{% postlist layout='" + bad_layout + "' %}"
        template = Template(template_string)
        context = Context({})
        with self.assertRaisesRegex(TemplateSyntaxError, f"The provided layout {bad_layout} is not a registered layout."):
            template.render(context)

    def test_default_layout_option(self):
        from blog_improved.templatetags.post_list import PostlistTag 
        from blog_improved.posts.post_list_markup_presets import layout_presets
        expected_layout = layout_presets["default"]
        self.assertEqual(expected_layout.rows, 3)
        self.assertEqual(expected_layout.columns, 3)
        actual_layout = PostlistTag._get_layout(self, "default")
        self.assertEqual(expected_layout, actual_layout)

    def test_postlisttag_runtime_register_layout(self):
        from blog_improved.posts.post_list_markup_presets import layout_presets
        from blog_improved.presentation import GridLayout

        new_layout = "yummy"
        layout_presets[new_layout] = GridLayout(rows=14, columns=11)
        template_string = "{% load blog_tags %}{% postlist layout='" + new_layout + "' %}"
        
        template = Template(template_string)
        context = Context({})
        template.render(context)
 

    def test_postlisttag_multiple_categories(self):
        expected_html = self.load_fixture("postlist_multiple_categories.html") 
        template_string = '{% load blog_tags %}{% postlist max_count="22" category="colors,programming" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
        # Parse both HTML strings
        expected = BeautifulSoup(expected_html, 'html.parser')
        rendered = BeautifulSoup(rendered_html, 'html.parser') 
        expected_list = expected.find(id="postlist")
        rendered_list = rendered.find(id="postlist")

        self.assertTrue(expected_list is not None)
        self.assertTrue(rendered_list is not None)
        # Count the number of <li> elements within the <ul>
        expected_post_count = PostlistTagTestCase.count_post_items(expected_list)
        rendered_post_count = PostlistTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_post_count, expected_post_count)
        expected_categories = expected_list.find_all("a", attrs={"rel": "category"})
        rendered_categories = rendered_list.find_all("a", attrs={"rel": "category"})
        expected_categories_count = len(expected_categories)        
        rendered_categories_count = len(rendered_categories)
        self.assertEqual(rendered_categories_count, expected_categories_count)
        for expected_cat, rendered_cat in zip(expected_categories, rendered_categories):
            self.assertTrue(expected_cat.text in ["colors","programming"])
            self.assertTrue(rendered_cat.text in ["colors","programming"])

    def test_postlisttag_featured(self):
        expected_html = self.load_fixture("postlist_featured.html")
        template_string = '{% load blog_tags %}{% postlist name="featured-news" featured="True" max_count="1" %}'
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
        self.assertEqual(rendered_article.find('h2').text, expected_article.find('h2').text)
        self.assertEqual(rendered_article.find('p').text, expected_article.find('p').text)
        expected_author = expected_article.find('address').find('a')
        rendered_author = rendered_article.find('address').find('a')
        self.assertEqual(rendered_author.text, expected_author.text)
        print(rendered_author)
        print("author")
        self.assertEqual(rendered_author["href"], expected_author["href"])

    def test_postlisttag_featured_and_ordinary_posts(self):
        expected_html = self.load_fixture("postlist_mix_feature_ordinary_posts.html")
        template_string = '{% load blog_tags %}{% postlist name="latest-news" featured="True" featured_count="2" max_count="5" %}'
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
        expected_post_count = PostlistTagTestCase.count_post_items(expected_list)

        rendered_post_count = PostlistTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_post_count, 5) 

        rendered_featured_count = len(rendered_list.find_all("article", attrs={"class": "article--featured"}))

        self.assertEqual(rendered_featured_count, 2) 


    def test_postlisttag_featured_and_feature_count(self):
        template_string = '{% load blog_tags %}{% postlist name="latest-news" featured="True" featured_count="2" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)

        # Parse both HTML strings
        rendered = BeautifulSoup(rendered_html, 'html.parser')
        # Check the `ul` element with id `latest-news__list`
        rendered_list = rendered.find(id="latest-news")

        self.assertTrue(rendered_list is not None)
        rendered_posts_count = PostlistTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_posts_count, 9) 
        rendered_featured_count = len(rendered_list.find_all("article", attrs={"class": "article--featured"}))

        self.assertEqual(rendered_featured_count, 2) 


    def test_postlisttag_empty_valeu_ignored_categories(self):
        template_string = '{% load blog_tags %}{% postlist ignore_category="" %}'
        template = Template(template_string)
        context = Context({})
        rendered_html = template.render(context)
   # Parse both HTML strings
        rendered = BeautifulSoup(rendered_html, 'html.parser')
        # Check the `ul` element with id `latest-news__list`
        rendered_list = rendered.find(id="postlist")
        self.assertTrue(rendered_list is not None)
        rendered_posts_count = PostlistTagTestCase.count_post_items(rendered_list)
        self.assertEqual(rendered_posts_count, 9) 

    def test_postlisttag_ignore_specific_category(self):
        # Render without ignoring any category
        template_string_all = '{% load blog_tags %}{% postlist %}'
        template_all = Template(template_string_all)
        context = Context({})
        rendered_html_all = template_all.render(context)
        rendered_all = BeautifulSoup(rendered_html_all, 'html.parser')

        # Count occurrences of the category class "article__category"
        category_elements = rendered_all.find_all(class_="article__category")
                # Count occurrences of the category class "article__category" containing the text "colors"
        category_elements = rendered_all.find_all(class_="article__category")
        total_categories = len(category_elements)
        total_color_categories = sum(1 for elem in category_elements if "colors" in elem.get_text(strip=True).lower())

        # Render with ignore_category="color"
        template_string_ignore = '{% load blog_tags %}{% postlist ignore_category="colors" %}'
        template_ignore = Template(template_string_ignore)
        rendered_html_ignore = template_ignore.render(context)
        rendered_ignore = BeautifulSoup(rendered_html_ignore, 'html.parser')

        # Check the `ul` element with id `postlist` still exists
        rendered_list_ignore = rendered_ignore.find(id="postlist")
        self.assertTrue(rendered_list_ignore is not None)

        # Count occurrences of "article__category" containing "colors" in the ignored list
        ignored_category_elements = rendered_ignore.find_all(class_="article__category")
        total_color_categories_ignored = sum(1 for elem in ignored_category_elements if "colors" in elem.get_text(strip=True).lower())

        # Ensure that after ignoring "colors," no articles have the "colors" category
        self.assertEqual(total_color_categories_ignored, 0)

    def test_default_layout_option(self):
        from blog_improved.templatetags.post_list import PostlistTag 
        from blog_improved.posts.posts import PostListQueryRequest
        def gaming_service(query):
            query.featured(True, 3).max_size(50)
        PostlistTag.service_filters.register_service("gaming", gaming_service)
        posts = PostListQueryRequest()

        self.assertEqual(posts._max_size, None)
        self.assertEqual(posts._featured, False)
        self.assertEqual(posts._num_featured, None)
        PostlistTag.service_filters.apply_service("gaming", posts)
        self.assertEqual(posts._max_size, 50)
        self.assertEqual(posts._num_featured, 3)
        self.assertEqual(posts._featured, True)

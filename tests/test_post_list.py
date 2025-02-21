from blog_improved.posts.posts import PostList 
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.formatters.html.html_generator import BlogHtmlFactory, HtmlGenerator, make_standard_element 
from blog_improved.posts.models import Post
from django.test import TestCase
from bs4 import BeautifulSoup

class TestBlogList(TestCase):
    fixtures = ["groups.yaml", "users.yaml", "media.yaml", "tags.yaml", "posts.yaml"]

    def test_create_bloglist(self):
        pl = PostList()
        # PostList is a type of list
        self.assertTrue(isinstance(pl, list))
        posts = Post.objects.all().values_list("id", "title")
        pl_with_param = PostList(posts) 
        ident, title = pl_with_param[0]
        self.assertTrue(isinstance(ident, int))
        self.assertTrue(isinstance(title, str))

    def test_post_list_with_items(self):
        posts = Post.objects.all().values_list("pk", "title", "headline", "author__username", "published_on", "content", "category__name", "is_featured", "slug")
        plist = PostList(posts)
        html = BlogHtmlFactory(HtmlGenerator(element_composer=make_standard_element))
        markup = PostListMarkup("post-list-test", plist, 3, 3, (50,25,25,), html)
        markup.build_grid()
        markup.generate_html()
        rendered = markup.get_rendered()
        soup = BeautifulSoup(rendered, "html.parser")
        # Find all elements with a class attribute containing "col-one-half" twice
        elements = soup.find_all(lambda tag: tag.has_attr("style") and tag["style"].count("width: 50%;") == 1)
        
        # Expect 3 col-one-half li items
        self.assertEqual(len(elements), 3)

        # Find all <ul> elements
        ul_elements = soup.find_all(class_="posts")
        # Count the number of cols items in each row
        for i, ul in enumerate(ul_elements):
            li_count = len(ul.find_all("div", {"class": "row"}))
            self.assertEqual(li_count, 3)

from blog_improved.posts.posts import PostList 
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.models import Post
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
        posts = Post.objects.all().values_list("title", "headline", "author__username", "published_on", "content", "category__name", "is_featured")
        plist = PostList(posts)
        markup = PostListMarkup("post-list-test", plist, 3, 3, (50,25,25,))
        rendered = markup.build_post_list().get_rendered()
        soup = BeautifulSoup(rendered, "html.parser")

        # Find all elements with a class attribute containing "col-one-half" twice
        elements = soup.find_all(lambda tag: tag.has_attr("class") and tag["class"].count("col-one-half") == 1)
        
        # Expect 3 col-one-half li items
        self.assertEqual(len(elements), 3)

        # Find all <ul> elements
        ul_elements = soup.find_all('ul')

        # Count the number of <li> items in each <ul>
        for i, ul in enumerate(ul_elements, start=1):
            li_count = len(ul.find_all('li'))
            self.assertEqual(i, 1)
            self.assertEqual(li_count, 9)

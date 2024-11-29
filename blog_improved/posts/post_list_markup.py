from blog_improved.utils.matrices import Matrix, create_matrix, LayoutMetrics, TraversalType, hasnext
from itertools import cycle
from dataclasses import dataclass
from blog_improved.helpers.html_generator import BlogHtmlFactory, HtmlGenerator
from blog_improved.themes.settings import get_theme
from blog_improved.posts.posts import PostList
from blog_improved import urls
from django.urls import reverse

g_theme = get_theme()

@dataclass
class ListCell:
    content: any
    width: float 
    height: float

class PostListMarkup:
    def __init__(self, name:str, posts: list, rows:int, columns:int, proportions:iter):
        if not rows or not columns:
            raise ValueError()

        self._name = name
        self._rows = rows
        self._columns = columns
        self._posts = posts
        self._proportions = proportions
        self._grid = list()
        self._rendered = None

    def add_list_item(self, porportion: int):
        pass

    def build_post_list(self):
        output = ""
        index = 0
        proportion = cycle(self._proportions)
        matrix = Matrix([], self._rows, self._columns)

        for i in range(self._rows * self._columns): 
            if i < len(self._posts):
                data = self._posts[i]
            else: 
                data = None

            item = ListCell(content = data,
                            width = next(proportion),
                            height = "fill"
                    )
            matrix.append(item)
            output += str(data)
            index += 1
        self._grid = matrix
        matrix = iter(matrix)
        html = BlogHtmlFactory(HtmlGenerator())
        parent = html.create_node("container", attributes={"class": g_theme.resolve_grid_class("container", None)})
        posts = []
        priority = iter(self._posts.get_priority_order())
        for item in matrix:
            if item.content is None:
                continue
            (
                    title, headline, author, publish_date, excerpt, category, featured
            ) = item.content
            author_url = reverse("user_profile", kwargs={"group": "author", "name": author})
            post = html.create_article(title, headline, author, author_url, publish_date, excerpt, category, featured)
            post.attributes["class"] += "article--featured" if next(priority) == PostList.PriorityOrder.FEATURE else ""
            posts.append(post)
        html_post_list = html.create_list(posts, self._name)
        for list_item, grid_cell in zip(html_post_list, self._grid):
            column_cls = g_theme.resolve_grid_class("column", grid_cell.width)
            list_item.attributes["class"] += column_cls
        parent.append(html_post_list)
        self._rendered = parent.render()
        return self 

    def get_rendered(self):
        return self._rendered

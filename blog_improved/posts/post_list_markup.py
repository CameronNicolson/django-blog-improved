from typing import Callable, List, Optional
from blog_improved.utils.matrices import Matrix, create_matrix, LayoutMetrics, TraversalType, hasnext
from blog_improved.utils.hetero_data_wrapper import HeteroDataWrapper
from dataclasses import dataclass
from blog_improved.helpers.html_generator import MarkupFactory, SgmlGenerator, SgmlNode
from blog_improved.themes.settings import get_theme
from blog_improved.posts.posts import PostList
from blog_improved.utils.strings import string_bound
from django.urls import reverse
from blog_improved.presentation.presentation_strategy import Rect

@dataclass
class ListCell:
    ident: int
    content: any
    width: float 
    height: float

class PostListMarkup:
    def __init__(self, name:str, posts: list, rows:int, columns:int, proportions:iter, sgml: MarkupFactory):
        if not rows or not columns:
            raise ValueError()
        if proportions is None:
           proportions = tuple(((100 / columns) for _ in range(1, columns)))
        self._name = name
        self._rows = rows
        self._columns = columns
        self._posts = posts
        self._proportions = proportions
        self._grid = list()
        self._rendered = None
        self._sgml = sgml
        self._container = None
        self._layouts = {
                "grid": self._default_layout,
                "list": self._flat_layout
        }
    
    def generate_item_title(self, text, hyperlink, level=1):
        """Generate a Post List's item HTML title."""
        sgml = self._sgml
        title_node = sgml.create_node(
            "heading", attributes={"class": f"posts--title h{level}"}, level=level
        )

        if hyperlink:
            link_node = sgml.create_node(
                "hyperlink",
                attributes={
                    "class": f"posts__title--link h{level}",
                    "href": hyperlink,
                },
            )
            title_node.add_child(link_node)
            link_node.add_child(sgml.create_node("text"))
        else:
            title_node.add_child(sgml.create_node("text"))

        return title_node

    def generate_post_link(self, link_type, **kwargs):
        """Generate a reverse URL for an article.""" 
        if link_type == "author":
            group = kwargs.get("group", "author")
            name = kwargs.get("name", None)
            try:
                return reverse("user_profile", kwargs={"group": group, "name": name}) 
            except Exception:
                return None
        elif link_type == "title":
            try:
                uri = kwargs.get("slug", None)
                return reverse("post_detail", kwargs={"slug": uri})
            except Exception:
                return None
        else:
            return None

    def build_grid(self):
        """Builds the grid structure for the post list."""
        from itertools import cycle
        from blog_improved.utils.matrices import Matrix

        proportion = cycle(self._proportions)
        matrix = Matrix([], self._rows, self._columns)

        for i in range(self._rows * self._columns):
            content = self._posts[i] if i < len(self._posts) else None
            matrix.append(
                ListCell(ident=i, content=content, width=next(proportion), height="fill")
            )

        self._grid = matrix

    def generate_html(self, layout_type: str = "grid"):
        """
        Generate HTML for the structured layout based on a layout type.
        """
        layout_strategy = self._layouts.get(layout_type)
        if layout_strategy is None:
            raise ValueError(f"Unknown layout type: {layout_type}")
        self.generate_html_str(layout_strategy=layout_strategy)

    def generate_html_str(self, layout_strategy: Optional[Callable[[List[List[ListCell]]], SgmlNode]] = None):
        """
        Generate HTML for the structured layout.
        A layout strategy determines how rows and cells are transformed into HTML nodes.
        """
        sgml = self._sgml
        if self._container is None:
            container = sgml.create_node("container")
            sgml.assign_class(container, "contaienr")
            self._container = container
        # Default layout strategy if none provided
        if layout_strategy is None:
            layout_strategy = self._default_layout

        posts_node = layout_strategy(self._grid)
        self._container.add_child(posts_node)
        self._rendered = self._container.render()

    def _default_layout(self, grid: List[List[ListCell]]) -> SgmlNode:
        """
        Default strategy: Each row becomes a <div>, and each cell becomes a <div> inside that row.
        """
        sgml = self._sgml
        parent_node = sgml.create_node("container")
        sgml.assign_identifier(parent_node, self._name)
        sgml.assign_class(parent_node, "posts")
        for row_number, row in enumerate(grid.rows()):
            row_node = sgml.create_node("container")
            sgml.assign_class(row_node, "row")
            for column_number, cell in enumerate(row):
                if cell.content:
                    article_node = self.create_post_article(cell) 
                    cell_node = sgml.create_node("container")
                    x = column_number * cell.width
                    x2 = x + cell.width
                    y = row_number * cell.height
                    y2 = y + cell.height 
                    pos = Rect(x, y, x2, y2)
                    sgml.move_position(cell_node, pos)
                    sgml.assign_class(cell_node, "posts__item")
                    cell_node.add_child(article_node)
                    row_node.add_child(cell_node)
            parent_node.add_child(row_node)

        return parent_node

    def _flat_layout(self, grid: List[List[ListCell]]) -> SgmlNode:
        """
        Flat layout strategy: All cells are treated as a single list (e.g., for <ul>/<li>).
        """
        sgml = self._sgml

        list_node = sgml.create_node("unordered_list", {
            "class": "posts list",
            "id":   f"{self._name}"  
        })

        for row in grid.rows():
            for cell in row:
                if cell.content:
                    article_node = self.create_post_article(cell)
                    list_item_node = sgml.create_node(
                        "list_item", {"class": "posts__item"}
                    )
                    list_item_node.add_child(article_node)
                    list_node.add_child(list_item_node)

        return list_node
    
    def create_post_article(self, cell: ListCell) -> SgmlNode:
        """Create an article node for a given cell."""
        sgml = self._sgml
        post_data = HeteroDataWrapper(cell.content, start=1)
        _, priority = self._posts.get_priority_order()[cell.ident]
        return sgml.create_article(
            title=post_data["title"],
            headline=post_data["headline"],
            author=post_data["author"],
            author_homepage=self.generate_post_link("author", name=post_data["author"]),
            date=post_data["published_on"],
            body_content=post_data["content"],
            category=post_data["category"],
            featured=(post_data["featured"] and priority == 0),
            article_url=self.generate_post_link("title", slug=post_data["slug"])
    )

    def get_rendered(self) -> str:
        """Return the rendered HTML."""
        if not self._rendered:
            raise ValueError("The post list has not been rendered yet.")
        return self._rendered


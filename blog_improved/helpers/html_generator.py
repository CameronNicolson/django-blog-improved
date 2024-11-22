from bigtree import Node
from typing import Optional, Callable, Dict, Any
from abc import ABC, abstractmethod 

class HtmlComponent:
    def __init__(self, 
        open_tag: Optional[Callable[..., str]] = None,
        close_tag: Optional[Callable[..., str]] = None,
        base_tag: Optional[str] = None,
        level_range: Optional[range] = None):

        self.open_tag = open_tag
        self.close_tag = close_tag
        self.level_range = level_range


class HtmlNode(Node):
    node_counter = 0

    def __init__(self, 
                 name: str,
                 component: HtmlComponent,
                 attributes: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(name=name, **kwargs)
        self.component = component
        self.attributes = attributes or {}
        self.children = []

    def add_child(self, node:Node):
        children = self.children + (node,)
        self.children = children

    def render(self) -> str:
        """Render the HTML node and its children recursively"""
        open_tag = self.component.open_tag(self.attributes) if self.component.open_tag else ""
        close_tag = self.component.close_tag() if self.component.close_tag else ""

        children_html = "".join(child.render() for child in self.children)
        return f"{open_tag}{children_html}{close_tag}"



class HtmlGenerator:

    def __init__(self):
        self._internal_count = 0
        self._components = {
            "hyperlink": make_standard_element('a'),
            'address': make_standard_element('address'),
            'article': make_standard_element('article'),
            'figure': make_standard_element('figure'),
            'div': make_standard_element('div'),
            'p': make_standard_element('p'), 
            'list': make_standard_element('ul'),
            'list_item': make_standard_element('li'),
            'ol': make_standard_element('ol'),
            'img': make_contained_element('img'),
            'br': make_contained_element('br'),
            "heading": make_hierarchical_element("h", range(1, 7)),
        }
    
    def create_node(self, 
                   tag_type: str, 
                   attributes: Optional[Dict[str, Any]] = None, 
                   **kwargs) -> HtmlNode:
        """Create a node with the appropriate component"""
        if tag_type not in self._components:
            raise ValueError(f"Unknown tag type: {tag_type}")
        name = tag_type
        component = self._components[tag_type]
        
        # Handle hierarchical elements (e.g., headings)
        if component.level_range:
            level = kwargs.get("level")
            if level is None:
                raise ValueError(f"Level is required for hierarchical elements like '{tag_type}'")
            if level not in component.level_range:
                raise ValueError(f"Invalid level {level} for '{tag_type}'. Must be in range {component.level_range}.")
            # Use level to modify the component dynamically
            name = f"{tag_type}{level}"
    # Use level to modify the component dynamically
            original_open_tag = component.open_tag
            original_close_tag = component.close_tag
            component = HtmlComponent(
                        open_tag=lambda attrs, level=level: original_open_tag(attrs, level) if original_open_tag else "",
                        close_tag=lambda level=level: original_close_tag(level) if original_close_tag else "",
                        level_range=component.level_range)
        self._increment_count()
        if attributes:
            node_name = attributes.get("id", self._internal_count)
        else:
            node_name = self._internal_count
        return HtmlNode(
            name=node_name,
            component=component,
            attributes=attributes
        )

    def _increment_count(self, n:int=1):
        result = self._internal_count + n
        self._internal_count = result

    def register_component(self, 
                         name: str, 
                         open_tag: Optional[Callable[..., str]] = None,
                         close_tag: Optional[Callable[..., str]] = None):
        """Register a new component type"""
        self._components[name] = HtmlComponent(open_tag, close_tag)

# Helper function for attribute formatting
def format_attributes(attrs: Optional[Dict[str, Any]] = None) -> str:
    if not attrs:
        return ""
    return " " + " ".join(f'{k}="{v}"' for k, v in attrs.items())


class MarkupFactory(ABC):
    @abstractmethod    
    def create_list(self, items):
        pass
    
    @abstractmethod
    def create_article(self, title: str, headline: str, author: str, date: str, body_content: str) -> HtmlNode:
        pass

class BlogHtmlFactory(MarkupFactory):
    def __init__(self, markup_generator: HtmlGenerator):
        self._markup = markup_generator

    def create_list(self, items, ident:str = ""):
        ident = ident + "__list" if ident else "list"
        list_node = self._markup.create_node("list", {"id": ident})
        for item in items:
            list_item = self._markup.create_node("list_item", 
            {"class": f"{ident}-item"})
            list_item.append(item)
            list_node.append(list_item)
        return list_node

    def create_article(self, title: str, headline: str, author: str, author_homepage:str, date: str, body_content: str) -> HtmlNode:
        article_node = self._markup.create_node("article")
        headings = enumerate(list((title,headline,)), start=1)
        for heading_level, heading_text in headings:
            if not heading_text:
                continue
            title_node = self._markup.create_node("heading", level=heading_level)
            title_node.add_child(TextNode(heading_text))
            article_node.add_child(title_node)

        author_node = self._markup.create_node("address", attributes={"class": "author"})
        author_contact = self._markup.create_node("hyperlink", attributes={"rel": f"{author}", "href": f"{author_homepage}", "class": "author__link"})
        author_contact.add_child(TextNode(f"{author}"))
        author_node.add_child(author_contact)

        article_node.add_child(author_node)

        return article_node

class TextNode(HtmlNode):
    def __init__(self, text: str, **kwargs):
        super().__init__(name="text", component=HtmlComponent(), **kwargs)
        self._text = text

    def render(self) -> str:
        return self._text

def make_contained_element(tag: str) -> HtmlComponent:
    """Factory for void elements like <img>, <br>, <input>"""
    return HtmlComponent(
        open_tag=lambda attrs: f"<{tag}{format_attributes(attrs)}/>",
        close_tag=None
    )

def make_standard_element(tag: str) -> HtmlComponent:
    """Factory for standard elements like <div>, <p>"""
    return HtmlComponent(
        open_tag=lambda attrs: f"<{tag}{format_attributes(attrs)}>",
        close_tag=lambda: f"</{tag}>"
    )

def make_hierarchical_element(tag: str, level_range: range) -> HtmlComponent:
    """Create a hierarchical component with level support."""
    if not level_range:
        raise ValueError("Level range must not be empty.")

    def open_tag(attrs: Optional[Dict[str, Any]], level:int) -> str:
        if level not in level_range:
            raise ValueError(f"Level {level} is outside the valid range: {level_range}")
        return f"<{tag}{level}{format_attributes(attrs)}>"

    def close_tag(level: int) -> str:
        if level not in level_range:
            raise ValueError(f"Level {level} is outside the valid range: {level_range}")
        return f"</{tag}{level}>"

    return HtmlComponent(
        open_tag=lambda attrs=None, level=None: open_tag(attrs, level) if level else "",
        close_tag=lambda level=None: close_tag(level) if level else "",
        level_range=level_range  # Save the range for potential future use
    )

from bigtree import Node
from typing import Optional, Callable, Dict, Any

class HtmlComponent:
    def __init__(self, 
                 open_tag: Optional[Callable[..., str]] = None,
                 close_tag: Optional[Callable[..., str]] = None):
        self.open_tag = open_tag
        self.close_tag = close_tag

class HtmlNode(Node):
    def __init__(self, 
                 name: str,
                 component: HtmlComponent,
                 attributes: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(name=name, **kwargs)
        self.component = component
        self.attributes = attributes or {}

# Example component definitions
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

class HtmlGenerator:
    def __init__(self):
        self._tree = None
        self.components = {
            'a': make_standard_element('a'),
            'figure': make_standard_element('figure'),
            'div': make_standard_element('div'),
            'p': make_standard_element('p'), 
            'ul': make_standard_element('ul'),
            'li': make_standard_element('li'),
            'ol': make_standard_element('ol'),
            'img': make_contained_element('img'),
            'br': make_contained_element('br'),
        }

    def create_node(self, 
                   tag_type: str, 
                   attributes: Optional[Dict[str, Any]] = None) -> HtmlNode:
        """Create a node with the appropriate component"""
        if tag_type not in self.components:
            raise ValueError(f"Unknown tag type: {tag_type}")
            
        return HtmlNode(
            name=tag_type,
            component=self.components[tag_type],
            attributes=attributes
        )

    def register_component(self, 
                         name: str, 
                         open_tag: Optional[Callable[..., str]] = None,
                         close_tag: Optional[Callable[..., str]] = None):
        """Register a new component type"""
        self.components[name] = HtmlComponent(open_tag, close_tag)

# Helper function for attribute formatting
def format_attributes(attrs: Optional[Dict[str, Any]] = None) -> str:
    if not attrs:
        return ""
    return " " + " ".join(f'{k}="{v}"' for k, v in attrs.items())


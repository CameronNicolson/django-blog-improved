import copy
from django.template.base import Node, NodeList, TextNode
from django.template.context import Context
from typing import Any, Callable, Union, Dict, List, Optional
from abc import ABC, abstractmethod 
from datetime import datetime as std_datetime
from blog_improved.sgml import SgmlAttributes

from blog_improved.utils.strings import (
    to_string_appender,
    normalise_extra_whitespace,
    validate_regex,
    strip_whitespace
)
from blog_improved.utils.time import convert_to_iso8601
from blog_improved.utils.urls import starts_with_uri    

@strip_whitespace
@normalise_extra_whitespace
@to_string_appender
def class_processor(value):
    return value

@strip_whitespace
@validate_regex(r'^[A-Za-z][A-Za-z0-9\-_:\.]*$')
def id_processor(value):
    return value

@strip_whitespace
def uri_processor(value):
    return value

def CDATA(value):
    return value

class SgmlComponent:
    def __init__(self, 
        tag:str = None,
        attrs:Optional[SgmlAttributes] = None,
        tag_omissions:str = None,
        level_range: Optional[range] = None):       
        
        self.tag = tag
        self.attrs = attrs
        self.tag_omissions = tag_omissions
        self.level_range = level_range

class SgmlNode(Node, ABC):
    def __init__(self, nodelist: NodeList=None):
        self.nodelist = nodelist or NodeList()  # Initialize the nodelist
    
    @abstractmethod
    def add_child(self, node):
        raise NotImplemented()

class HtmlNode(SgmlNode):
    node_counter = 0

    def __init__(self, 
                 name: str,
                 component: SgmlComponent,
                 attributes: Optional[SgmlAttributes] = None,
                 **kwargs):
        super().__init__()
        self.component = component
        self.child_counts = dict()
   
    @property
    def attrs(self):
        return self.component.attrs

    def add_child(self, node:Node):
        # comply with the occurence policy
        #occurrence_rule = self.component.definition.occurence or "*"
       # current_count = self.child_counts.get(node.name, 0)

        #num_occurence = self.occurence.get(node.name, None)
        # Enforce occurrence rules
        #if occurrence_rule == "?" and current_count >= 1:
        #    raise ValueError(f"Element '{node.name}' can only appear once.")
        #elif occurrence_rule == "+" and current_count == 0:
        #    pass  # Adding first occurrence is valid
        #elif occurrence_rule == "+" and current_count >= 1:
        #    pass  # Adding repeated occurrences is valid
        #elif occurrence_rule == "*" and current_count >= 0:
        #    pass  # Adding any number of occurrences is valid
        #else:
        #    raise ValueError(f"Invalid occurrence '{occurrence_rule}' for '{node.name}'.")

        # self.child_counts[node.name] = current_count + 1
        self.nodelist.append(node)
    
    def get_style_class(self) -> list[str]:
        classes = []
        if self.attributes:
          classes = self.attributes.get("class", None)
        if classes:
            return classes.get_as_list()
        return classes

    def open_tag(self):
        # clean spaces between chars
        omission_parts = self.component.tag_omissions.replace(" ", "")
        omission = omission_parts[0] 
        if omission in ["-", "0"]:
            return self.component.tag
        return None

    def end_tag(self):
        omission_parts = self.component.tag_omissions.replace(" ", "")
        omission = omission_parts[1] 
        if omission in ["-", "0"]:
            return self.component.tag
        return None

    def render(self, context: Context=Context(), open_tag=True, end_tag=True) -> str:
        """Render the HTML node and its children recursively"""
        if open_tag:
            open_tag = self.open_tag() 
        else:
            open_tag = ""
        if self.component.attrs:
            attributes = format_attributes(self.component.attrs)
        else:
            attributes = ""
        if end_tag:
            end_tag = self.end_tag()
        else:
            end_tag = ""
        context = Context(dict_=None, autoescape=True, use_l10n=None, use_tz=None)

        children = "".join(child.render(Context({})) for child in self.nodelist)
        #children = self.nodelist.render(context)

        return f"<{open_tag}{attributes}>{children}</{end_tag}>"

class SgmlGenerator(ABC):

    @abstractmethod
    def create_node(self, 
                   tag_type: str, 
                   attributes: Optional[Dict[str, Any]] = None,
                   **kwargs) -> SgmlNode:
        """Create a node with the appropriate component"""
        raise NotImplemented()
   
    @abstractmethod
    def register_component(self, 
                         name: str, 
                         open_tag: Optional[Callable[..., str]] = None,
                         close_tag: Optional[Callable[..., str]] = None):
        raise NotImplemented()

    @abstractmethod
    def remove_component(self, component_name):
        raise NotImplemented()

    @abstractmethod
    def get_registered_components(self):
        raise NotImplemented()

COREATTRS = {"id": id_processor, "class": class_processor, "style": CDATA}


class HtmlGenerator(SgmlGenerator):
    def __init__(self, element_composer: Callable[[str, dict, str], SgmlComponent]):
        self._element_composer = element_composer
        self._internal_count = 0
        self._components = {
                "hyperlink": self._element_composer("a", {"id": id_processor, "class": class_processor, "href": uri_processor, "rel": CDATA  }),
            "address": self._element_composer("address", COREATTRS),
            "article": self._element_composer("article", COREATTRS),
            "figure": self._element_composer("figure", COREATTRS),
            "container": self._element_composer("div", COREATTRS),
            "inline_container": self._element_composer("span", COREATTRS),
            "paragraph": self._element_composer("p", COREATTRS), 
            "list": self._element_composer("ul", COREATTRS),
            "list_item": self._element_composer("li", COREATTRS),
            "ordered_list": self._element_composer("ol", COREATTRS),
            "image": self._element_composer("img", COREATTRS),
            "vertical-space": self._element_composer("br", COREATTRS, tag_omissions="- O"),
            "heading": make_hierarchical_element("h1|h2|h3|h4|h5|h6", COREATTRS),
            "time": self._element_composer("time", {"id": id_processor, "datetime": convert_to_iso8601, "class": class_processor}),
        }
    
    def create_node(self, 
                   tag_type: str, 
                   attributes: Optional[Dict[str, Any]] = None, 
                   **kwargs) -> HtmlNode:
        """Create a node with the appropriate component"""
        if tag_type not in self._components:
            raise ValueError(f"Unknown tag type: {tag_type}")
        component = self._components[tag_type]
        node_name = "" 
        new_attrs = copy.deepcopy(component.attrs)
        new_component = SgmlComponent(
                tag=component.tag,
                attrs=new_attrs,

                tag_omissions=component.tag_omissions,
            )
        if attributes:
            node_name = attributes.get("id", self._internal_count)
            new_component.attrs.update(attributes)
        else:
            node_name = self._internal_count

      
        # If hierarchical, adjust component tag based on level
        if component.level_range:
            level = kwargs.get("level")
            if level is None:
                raise ValueError(f"Level is required for hierarchical elements like '{tag_type}'")
            if level not in component.level_range:
                raise ValueError(f"Invalid level {level} for '{tag_type}'. Must be in range {component.level_range}.")

            # Split tags and choose the correct one
            all_tags = component.tag.split("|")
            chosen_tag = all_tags[level - 1]
            new_component = SgmlComponent(
                tag=chosen_tag,
                attrs=new_attrs,
                tag_omissions=component.tag_omissions,
                level_range=component.level_range,
            )

        self._increment_count()
 
        return HtmlNode(
            name=node_name,
            component=new_component,
        )

    def _increment_count(self, n:int=1):
        result = self._internal_count + n
        self._internal_count = result

    def register_component(self, name: str, component_factory: Callable):
        """Register a new component type"""
        self._components[name] = component_factory

    def remove_component(self, name: str):
        if name in self._components:
            del self._components[name]

    def get_registered_components(self):
        return self._components

# Helper function for attribute formatting
def format_attributes(attrs: Optional[Dict[str, Any]] = None) -> str:
    if not attrs:
        return ""
    return " " + " ".join(f'{k}="{v}"'.replace("\'", "")  for k, v in attrs.items() if v is not None)


class MarkupFactory(ABC):
    @abstractmethod    
    def create_list(self, items):
        pass
    
    @abstractmethod
    def create_article(self, title: str, headline: str, author: str, date: str, body_content: str) -> SgmlNode:
        pass

    @abstractmethod
    def create_node(self, tag_type: str, attributes: Optional[Dict[str, Any]] = None, **kwargs) -> SgmlNode:
        pass

    @abstractmethod
    def apply_presentation_attributes(self, sgml_element, width: int, height: int):
        """Applies platform-specific presentation attributes to the SGML element."""
        raise NotImplementedError("Subclasses must implement this method.")
 

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

    def create_article(self, title: str, headline: str, author: str, author_homepage:str, date: std_datetime, body_content: str, category:str, featured:bool, article_url:str) -> HtmlNode:

        from blog_improved.helpers.hyperlink_wrapper import hyperlink_wrapper
        article_node = self._markup.create_node("article", attributes={"class": "article"})
        if featured:
            article_node.attrs["class"] += "article--featured"
        
        if title:
            title_node = self._markup.create_node("heading", attributes={"class": "article__title"}, level=1)
            title_text_node = TextNode(title)
            title_text_node = hyperlink_wrapper(self._markup, article_url, title_text_node)
            title_node.add_child(title_text_node)
            article_node.add_child(title_node)

        if headline: 
            headline_node = self._markup.create_node("heading", attributes={"class": "article__headline"}, level=2)
            headline_node.add_child(TextNode(headline))
            article_node.add_child(headline_node)

        meta_node = self._markup.create_node("container", attributes={"class": "article__meta"})

        if author: 
            author_node = self._markup.create_node("address", attributes={"class": "article__author"})
            author_text_node = TextNode(f"{author}")
            author_text_node = hyperlink_wrapper(self._markup, author_homepage, author_text_node)
            author_node.add_child(author_text_node)
            meta_node.add_child(author_node)

        if date:
            datetime_node = self._markup.create_node("time", {"class": "article__time--published-date", "datetime": date})
            datetime_node.add_child(TextNode(date.strftime("%d %B %Y")))
            meta_node.add_child(datetime_node)
        
        if category:
            divider_text_node = TextNode(" - ")
            category_text_node = TextNode(category)
            category_text_node = hyperlink_wrapper(self._markup, category, category_text_node)
            try:
                category_text_node.attrs["rel"] = "category"
            except:
                pass
            meta_node.add_child(divider_text_node)
            meta_node.add_child(category_text_node)

        if len(meta_node.nodelist) > 0:
            article_node.add_child(meta_node)

        return article_node

    def create_node(self, tag_type: str, attributes: Optional[Dict[str, Any]] = None, **kwargs) -> HtmlNode:
        """Delegate node creation to the internal HtmlGenerator."""
        return self._markup.create_node(tag_type, attributes, **kwargs)

    def apply_presentation_attributes(self, sgml_element, width: int, height: int):
        if width:
            sgml_element.attrs["style"] = sgml_element.attrs.get("style", ""
            ) + f" width: {width}%;"
        if height:
            sgml_element.attrs["style"] = sgml_element.attrs.get("style", ""
                ) + f" height: {height}%;"


def make_standard_element(name: str, attrs:dict, attrs_defaults=None, tag_omissions:str="--") -> SgmlComponent:
    """Factory for void elements like <img>, <br>, <input>"""
    attrs = SgmlAttributes(attributes_def=attrs, initial_values=attrs_defaults)
    return SgmlComponent(
        tag=name,
        attrs=attrs,
        tag_omissions=tag_omissions
    )


def make_hierarchical_element(tags: str, attrs: Dict[str, Callable]) -> SgmlComponent:
    """
    Create a hierarchical component with level support.
    `tags` is a string like "H1|H2|H3|H4|H5|H6".
    """
    name_list = tags.split("|")
    level_range = range(1, len(name_list) + 1)
    attrs = SgmlAttributes(attributes_def=attrs)
    return SgmlComponent(
        tag=tags,  # Store all possible tags here, separated by |
        attrs=attrs,
        tag_omissions="--",
        level_range=level_range
    )


import copy
from typing import Any, Callable, Union, Dict, List, Optional
from abc import ABC, abstractmethod 
from datetime import datetime as std_datetime
from blog_improved.sgml import ChoiceContentModel, ContentModel, ElementDefinition, EntityDefinition, LiteralStringValue, OmissionRule, RepetitionControl, SgmlAttributes
from blog_improved.utils.strings import (
    to_string_appender,
    normalise_extra_whitespace,
    validate_regex,
    strip_whitespace
)
from blog_improved.utils.time import convert_to_iso8601
from blog_improved.utils.urls import starts_with_uri    
from blog_improved.utils.math import RangeClamper
from blog_improved.presentation.presentation_strategy import PresentationStrategy, Rect
from ..markup import MarkupFactory, MarkupNode
from blog_improved.sgml.sgml import SgmlComponent


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

class TextNode(MarkupNode):
    markup_format = "plaintext"

    def __init__(self, text):
        print(text)
        self._text = text

    def render(self) -> str:
        return self._text

class HtmlNode(MarkupNode):
    node_counter = 0
    markup_format = "html"

    def __init__(self, 
                 name: str,
                 component: SgmlComponent,
                 **kwargs):
        super().__init__()
        self.component = component
        self._children:List[HtmlNode] = []
        self.child_counts = dict()
        self._parent = None
   
    @property
    def attrs(self):
        return self.component.attrs
   
    @property
    def children(self):
        return self._children 

    @property
    def parent(self):
        return self._child

    @parent.setter
    def parent(self, node):
        self._parent = node
  
    def add_child(self, child):
        self._children.append(child)
        child.parent = self

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

    def render(self) -> str:
        """Render the HTML node and its children recursively"""
        open_tag = self.open_tag() 
        if self.component.attrs:
            attributes = format_attributes(self.component.attrs)
        else:
            attributes = ""

        end_tag = self.end_tag()
        
        children_strings = []  # List to store the rendered children as strings

        for child in self.children:
            rendered_child = child.render()  # Get the rendered output (could be an object)

            print(f"Child type: {type(child)}")
            print(f"Rendered child type: {type(rendered_child)}")
            print(f"Rendered child: {rendered_child}")  # Print the rendered output
            print(f"Rendered child (string): {str(rendered_child)}")  # Print string conversion

            children_strings.append(str(rendered_child))  # Convert to string and add to list

            children = "".join(children_strings)  # Join the strings at the end


        return f"<{open_tag}{attributes}>{children}</{end_tag}>"

class SgmlGenerator(ABC):

    @abstractmethod
    def create_node(self, 
                   tag_type: str, 
                   attributes: Optional[Dict[str, Any]] = None,
                   **kwargs) -> MarkupNode:
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

ELEMENTS = {
    "a": ElementDefinition(name="A", content=ContentModel(elements=["%inline;"], group_repetition=RepetitionControl("*")), tag_omission_rules=OmissionRule("-", "-")),
    "address": ElementDefinition(name="ADDRESS", content=ContentModel(elements=["%inline;"], group_repetition=RepetitionControl("*")), 
                tag_omission_rules=OmissionRule("-", "-")
            ),
    "article": ElementDefinition(name="ARTICLE", content=ContentModel(elements=["%flow;"], group_repetition=RepetitionControl("*")),
                                 tag_omission_rules=OmissionRule("-", "-")),
    "div": ElementDefinition(name="DIV", content=ContentModel(elements=["%flow;"], group_repetition=RepetitionControl("*")),
                             tag_omission_rules=OmissionRule("-", "-")),
    "span": ElementDefinition(name="SPAN", content=ContentModel(elements=["%inline;"], group_repetition=RepetitionControl("*")), tag_omission_rules=OmissionRule("-", "-")
        ),
    "heading": ElementDefinition(EntityDefinition(
            "heading",
           LiteralStringValue(components=[ChoiceContentModel(elements=["H1", "H2", "H3", "H4", "H5", "H6"], group_repetition=RepetitionControl(""))]),
            parameter=True
        ),
            OmissionRule("-", "-"),
            ContentModel(elements=["%inline;"], group_repetition=RepetitionControl("*")),
        ),
    "time": ElementDefinition(name="TIME", content=ContentModel(elements=["%Datetime;"]), tag_omission_rules=OmissionRule("-", "-")
                              ),

    "p": ElementDefinition(name="P", content=ContentModel(elements=["%inline;"], group_repetition=RepetitionControl("*")), tag_omission_rules=OmissionRule("-", "O")),
    "ul": ElementDefinition(name="UL", content=ContentModel(elements=["LI"], group_repetition=RepetitionControl("+")), tag_omission_rules=OmissionRule("-", "-")),
    "li": ElementDefinition(name="LI", content=ContentModel(elements=["%flow;"], group_repetition=RepetitionControl("*")), tag_omission_rules=OmissionRule("-", "O")),
    }


class HtmlGenerator(SgmlGenerator):
    def __init__(self, element_composer: Callable[[str, dict, str], SgmlComponent]):
        self._element_composer = element_composer
        self._internal_count = 0
        self._components = {
                "hyperlink": self._element_composer(ELEMENTS["a"], {"id": id_processor, "class": class_processor, "href": uri_processor, "rel": CDATA  }),
            "address": self._element_composer(ELEMENTS["address"], COREATTRS),
            "article": self._element_composer(ELEMENTS["article"], COREATTRS),
            "container": self._element_composer(ELEMENTS["div"], COREATTRS),
            "inline_container": self._element_composer(ELEMENTS["span"], COREATTRS),
            "paragraph": self._element_composer(ELEMENTS["p"], COREATTRS), 
            "unordered_list": self._element_composer(ELEMENTS["ul"], COREATTRS),
            "list_item": self._element_composer(ELEMENTS["li"], COREATTRS),
            #            "ordered_list": self._element_composer("ol", COREATTRS),
            #            "image": self._element_composer("img", COREATTRS),
            #            "vertical-space": self._element_composer("br", COREATTRS, tag_omissions="- O"),
            "heading": make_hierarchical_element(ELEMENTS["heading"], COREATTRS),
            "time": self._element_composer(ELEMENTS["time"], {"id": id_processor, "datetime": convert_to_iso8601, "class": class_processor}),
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
            all_tags = [n for n in component.tag]
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


class BlogHtmlFactory(MarkupFactory):
    def __init__(self, 
                markup_generator: HtmlGenerator,
                presentation_strategy: PresentationStrategy = None):
        self._markup = markup_generator
        self._presentation = presentation_strategy or InlinePresentationStrategy()

    def assign_identifier(self, element: SgmlComponent, 
                          ident: str):
        if not ident or not element:
            raise ValueError() 
        element.attrs["id"] = ident

    def assign_class(self, element: SgmlComponent, classname: str):
        if not classname or not element:
            raise ValueError()
        try:
            original_class = element.attrs.get("class", None)
            if not original_class:
                element.attrs["class"] = ""
            element.attrs["class"] += classname

        except KeyError: 
            raise KeyError("Element does not support class attribute")
        
    def create_list(self, items, ident:str = ""):
        ident = ident + "__list" if ident else "list"
        list_node = self._markup.create_node("unordered_list", {"id": ident})
        for item in items:
            list_item = self._markup.create_node("list_item", 
            {"class": f"{ident}-item"})
            list_item.append(item)
            list_node.append(list_item)
        return list_node

    def create_article(self, title: str, headline: str, author: str, author_homepage:str, date: std_datetime, body_content: str, category:str, featured:bool, article_url:str) -> HtmlNode:
        from blog_improved.utils.sgml import bool_wrapper

        article_node = self._markup.create_node("article", attributes={"class": "article"})
        if featured:
            article_node.attrs["class"] += "article--featured"
        
        if title:
            title_node = self._markup.create_node("heading", attributes={"class": "article__title"}, level=2)
            title_text_node = TextNode(title)
            title_text_node = bool_wrapper(self._markup, article_url, "hyperlink", {"href": article_url, "class": "article__title-link"}, title_text_node)
            title_node.add_child(title_text_node)
            article_node.add_child(title_node)

        if headline: 
            headline_node = self._markup.create_node("paragraph", attributes={"class": "article__headline"})
            headline_node.add_child(TextNode(headline))
            article_node.add_child(headline_node)

        meta_node = self._markup.create_node("container", attributes={"class": "article__meta"})

        if author: 
            author_node = self._markup.create_node("address", attributes={"class": "article__author"})
            author_text_node = TextNode(f"{author}")
            author_text_node = bool_wrapper(self._markup, author_homepage, "hyperlink", {"href": author_homepage}, author_text_node)

            author_node.add_child(author_text_node)
            meta_node.add_child(author_node)

        if date:
            datetime_node = self._markup.create_node("time", {"class": "article__time--published-date", "datetime": date})
            datetime_node.add_child(TextNode(date.strftime("%d %B %Y")))
            context_node = self._markup.create_node("inline_container", {"class": "visually-hidden"})
            context_node.add_child(TextNode("Posted on:"))
            meta_node.add_child(context_node)
            meta_node.add_child(datetime_node)
        
        if category:
            divider_text_node = TextNode(" - ")
            category_text_node = TextNode(category)
            category_text_node = bool_wrapper(self._markup, article_url, "hyperlink", {"href": category, "class": "article__category article__category--link"}, category_text_node)
            try:
                category_text_node.attrs["rel"] = "category"
            except:
                category_inline_container = self._markup.create_node("inline_container", {"class": "article__category"})
                category_inline_container.add_child(category_text_node)
            meta_node.add_child(divider_text_node)
            context_node = self._markup.create_node("inline_container", {"class": "visually-hidden"})
            context_node.add_child(TextNode("In the category:"))
            meta_node.add_child(context_node)
            meta_node.add_child(category_text_node)

        if len(meta_node.children) > 0:
            article_node.add_child(meta_node)

        return article_node

    def create_node(self, tag_type: str, attributes: Optional[Dict[str, Any]] = None, **kwargs) -> HtmlNode:
        """Delegate node creation to the internal HtmlGenerator."""
        return self._markup.create_node(tag_type, attributes, **kwargs)

    def move_position(self, element: SgmlComponent, pos: Rect):
        self._presentation.move_position(element, pos) 
        

def make_standard_element(element: ElementDefinition, attrs:dict, attrs_defaults=None, tag_omissions:str="--") -> SgmlComponent:
    """Factory for void elements like <img>, <br>, <input>"""
    attrs = SgmlAttributes(attributes_def=attrs, initial_values=attrs_defaults)
    return SgmlComponent(
        tag=element.name,
        attrs=attrs,
        tag_omissions=tag_omissions
    )

def make_hierarchical_element(element: ElementDefinition, attrs: Dict[str, Callable]) -> SgmlComponent:
    """
    Create a hierarchical component with level support.
    `tags` is a string like "H1|H2|H3|H4|H5|H6".
    """
    num_element_options = sum(1 for _ in element.name) 
    level_range = range(1, num_element_options)
    attrs = SgmlAttributes(attributes_def=attrs)
    return SgmlComponent(
        tag=element.name,
        attrs=attrs,
        tag_omissions="--",
        level_range=level_range
    )

def get_width_map():
    """Default logic that returns some standard width map."""
    return {
        8.33: "col-1",
        16.66: "col-2",
        33: "col-4",
        99.96: "col-12"
    }

def get_grid_config():
    return { 
        "container": "container", 
        "column": "col", 
        "row": "row", 
        "allowed_offset": 10,
    }

def build_strategy():
    if True:
        css_modifier = CssElementModifier(CssPresentation())
        grid = get_grid_config()
        width_map = get_width_map()
        clamp = RangeClamper()
        build_strategy = GridClassName(css_modifier, grid, width_map, clamp)
        return build_strategy
    else:
        return InlinePresentationStrategy()

def create_blog_html_factory():
    from django.apps import apps
    config = apps.get_app_config("blog_improved")
    sgml_generator = config.sgml_generator
    strategy = build_strategy()
    return BlogHtmlFactory(sgml_generator, 
                           presentation_strategy=strategy)

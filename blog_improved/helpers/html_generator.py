import copy
from django.template.base import Node, NodeList, TextNode
from django.template.context import Context
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
from blog_improved.presentations.presentation_strategy import PresentationStrategy, Rect


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
            #            "list": self._element_composer("ul", COREATTRS),
            #            "list_item": self._element_composer("li", COREATTRS),
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


class MarkupFactory(ABC):
    @abstractmethod
    def assign_identifier(self, ident:str):
        """Applies an ID attribute to the SGML element."""
        raise NotImplementedError("Subclasses must implement this method.")
 
    @abstractmethod
    def assign_class(self, element: SgmlComponent, classname: str):
        raise NotImplementedError("Subclasses must implement this method.")

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
    def move_position(self, sgml_element, pos: Rect):
        """Applies platform-specific presentation attributes to the SGML element."""
        raise NotImplementedError("Subclasses must implement this method.")
 

class InlinePresentationStrategy(PresentationStrategy):
    """
    A strategy that applies basic inline styles directly.
    """

    def move_position(self, sgml_element, pos: Rect):
        width = pos.width
        if width:
            current_style = sgml_element.attrs.get("style", "")
            sgml_element.attrs["style"] = f"{current_style} width: {pos.width}%;"

class CssPresentation(PresentationStrategy):
    def move_position(self, sgml_element, pos: Rect) -> SgmlComponent:
        return sgml_element

class CssElementModifier(CssPresentation): 
    def __init__(self, css_presentation):
        self._presentation = css_presentation

    def move_position(self, sgml_element, pos: Rect) -> SgmlComponent:
        return self._presentation.move_position(sgml_element, pos)

class WidthClassName(CssElementModifier):
    """
    A strategy that applies classname (based on numeric width)
    """

    def __init__(self, presentation, width_scale: dict[float, str]):
        super().__init__(presentation)  # Call parent constructor
        self.width_scale = width_scale

    def move_position(self, sgml_element, pos: Rect) -> SgmlComponent:
        element = self._presentation.move_position(sgml_element, pos)
        # Possibly find the matching class if width is given:
        chosen_class = element.attrs["class"] or ""
        width = pos.width
        for threshold, classname in self.width_scale.items():
            # pick the nearest threshold or however your matching logic works
            if width <= threshold:
                chosen_class += classname
                break

        if bool(chosen_class):
            element.attrs["class"] = f"{chosen_class}"
        return element

class GridClassName(CssElementModifier):
    """
    A strategy that applies classname (based on numeric width)
    """

    def __init__(self, presentation, grid_config, width_scale, clamp):
        super().__init__(presentation)  # Call parent constructor
        self._width_scale = width_scale
        self._grid_config = grid_config
        self._clamp = clamp

    def _resolve_grid_class(self, role, size):
        """
        Resolve a grid class for a given role (e.g., row, column) and scale.

        :param role: The grid role to resolve (e.g., "row" or "column").
        :param scale: The scale to apply for roles that support it (e.g., column widths).
        :return: A string representing the CSS class.
        """
        if role not in self._grid_config:
            raise ValueError(f"Unknown grid role: {role}")

        if size is None:  # Roles like 'row' may not require scale
            return self._grid_config[role]

        width_str = self._find_width(size)
        if not width_str:
            raise ValueError(f"Invalid size: {size}")
        return f"{self._grid_config[role]}-{width_str}"

    def _find_width(self, value):
        """
        Find the nearest width class for a given value, with negotiation
        for out-of-range values.

        :param value: The input size value.
        :return: The matching width class or None.
        """
        if not isinstance(value, (int, float, complex)):
            raise ValueError("Expected a number type")

        # Adjust value if it's beyond the highest scale
        min_value = min(self._width_scale.keys()) 
        max_value = max(self._width_scale.keys())
        negotiated_value = self._clamp.negotiate(value, min_value, max_value)

        if negotiated_value is None:
            return None

        # Find the nearest width class for the negotiated value
        prev = None
        for i, width in enumerate(sorted(self._width_scale.keys())):
            if i == 0:
                prev = width
            if negotiated_value == width:
                return self._width_scale[width]
            elif negotiated_value >= prev and negotiated_value < width:
                return self._width_scale[prev]
            prev = width
        return self._width_scale[max_value]  # Fallback to the max class
 

    def _get_column_class(self, value):
        column_str = self._grid_config.get("column", "")
        width_str = self._find_width(value)
        width_str = "-" + width_str if width_str else ""  
        return column_str + width_str

    def move_position(self, sgml_element, pos: Rect) -> SgmlComponent:
        element = self._presentation.move_position(sgml_element, pos)
        # Possibly find the matching class if width is given:
        column_cls = self._resolve_grid_class("column", pos.width)
        chosen_cls = element.attrs["class"] or ""
        chosen_cls += f"{column_cls}"
        element = sgml_element.attrs["class"] = chosen_cls
        return element


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
        list_node = self._markup.create_node("list", {"id": ident})
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
            category_text_node = bool_wrapper(self._markup, article_url, "hyperlink", {"href": category, "class": "article__category-link"}, category_text_node)
            try:
                category_text_node.attrs["rel"] = "category"
            except:
                pass
            meta_node.add_child(divider_text_node)
            context_node = self._markup.create_node("inline_container", {"class": "visually-hidden"})
            context_node.add_child(TextNode("In the category:"))
            meta_node.add_child(context_node)
            meta_node.add_child(category_text_node)

        if len(meta_node.nodelist) > 0:
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

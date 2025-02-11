from typing import Any, Dict, Optional
from abc import ABC, abstractmethod 
from blog_improved.sgml.sgml import SgmlComponent
from blog_improved.presentation.presentation_strategy import Rect
from django.utils.tree import Node

class MarkupNode(ABC):
    @property
    @abstractmethod
    def markup_format(self):
        """Subclasses must define a name attribute."""
        pass

    def add_child(self, child):
        raise NotImplementedError("Subclasses must implement this method.")

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
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def create_article(self, title: str, headline: str, author: str, date: str, body_content: str) -> Node:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def create_node(self, tag_type: str, attributes: Optional[Dict[str, Any]] = None, **kwargs) -> Node:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def move_position(self, sgml_element, pos: Rect):
        """Applies platform-specific presentation attributes to the SGML element."""
        raise NotImplementedError("Subclasses must implement this method.")
 

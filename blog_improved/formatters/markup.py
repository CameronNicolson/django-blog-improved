from enum import Enum
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod 
from blog_improved.sgml.sgml import SgmlComponent
from blog_improved.presentation.presentation_strategy import Rect
from django.utils.tree import Node

class CaseSensitivity(Enum):
    SENSITIVE = "sensitive"       # Case-sensitive (e.g., "Node" != "node")
    INSENSITIVE = "insensitive"   # Case-insensitive (e.g., "Node" == "node")
    UPPERCASE_ONLY = "uppercase"  # Treats only uppercase as significant
    LOWERCASE_ONLY = "lowercase"  # Treats only lowercase as significant

class MarkupNode(ABC):
    @property
    @abstractmethod
    def children(self):
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    @abstractmethod
    def case_sensitivity(self) -> CaseSensitivity:
        pass
    
    def compare_case(self, other: str) -> bool:
        """Compare the node's value with another string based on its case sensitivity setting."""
        if self.case_sensitivity == CaseSensitivity.INSENSITIVE:
            return True
        elif self.case_sensitivity == CaseSensitivity.UPPERCASE_ONLY:
            return other.upper() == other
        elif self.case_sensitivity == CaseSensitivity.LOWERCASE_ONLY:
            return other.islower()
        return True  # Case-sensitive comparison

    @property
    @abstractmethod
    def markup_format(self):
        """Subclasses must define a name attribute."""
        raise NotImplementedError("Subclasses must implement this method.")

    def add_child(self, child):
        raise NotImplementedError("Subclasses must implement this method.")

    def render(self):
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
 

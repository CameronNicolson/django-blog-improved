from typing import Any, Callable, Union, Dict, List, Optional
from dataclasses import dataclass

class EntityRegistry:
    """Manages registration and lookup of parameter entities."""
    def __init__(self):
        self.registry: Dict[str, str] = {}

    def register(self, name: str, value: str):
        """Register a parameter entity with a name and value."""
        self.registry[name] = value

    def resolve(self, name: str) -> Optional[str]:
        """Resolve a parameter entity by name."""
        return self.registry.get(name)

@dataclass
class OmissionRule:
    start_tag: str  # Either '-' (required) or 'O' (optional)
    end_tag: str    # Either '-' (required) or 'O' (optional)

    def __post_init__(self):
        # Validate the inputs
        valid_values = {"-", "O"}
        if self.start_tag not in valid_values or self.end_tag not in valid_values:
            raise ValueError("Omission rules must be '-' (required) or 'O' (optional).")

    def __str__(self):
        # Concatenate start and end tag rules
        return f"{self.start_tag} {self.end_tag}"

@dataclass
class RepetitionControl:
    """Represents a repetition operator."""
    operator: str  # One of '*', '+', '?'

    def __str__(self):
        return str(self.operator)

@dataclass
class ContentModel:
    """Represents a generic content model."""
    elements: List[Union[str, "ContentModel", "RepetitionControl"]]
    group_repetition: Optional[RepetitionControl] = None  # Repetition applied to the group

    def _wrap_with_repetition(self, content: str) -> str:
        """
        Wraps the content in parentheses if group_repetition exists and applies the repetition operator.
        """
        if self.group_repetition:
            return f"({content}){self.group_repetition}"
        return f"({content})"

    def __str__(self):
        elements_str = " ".join(str(e) for e in self.elements)
        return self._wrap_with_repetition(elements_str)

    def evaluate(self, registry: EntityRegistry) -> str:
        def resolve_element(el):
            if isinstance(el, str) and el.startswith("%") and el.endswith(";"):
                param_name = el[1:-1]
                return registry.resolve(param_name) or el
            return str(el)
        elements_str = ", ".join(resolve_element(e) for e in self.elements)
        if self.group_repetition:
            return f"({elements_str}){self.group_repetition}"
        return elements_str

@dataclass
class EmptyContentModel:
    """Represents an empty content model."""

@dataclass
class SequenceContentModel(ContentModel):
    """Represents a sequence content model."""
    elements: List[Union[str, "RepetitionControl"]]

    def __str__(self):
        element_str = "".join(
        str(val) if not isinstance(val, RepetitionControl) else str(val) + ","
        for val in self.elements
        ).rstrip(",")
        return self._wrap_with_repetition(element_str)

@dataclass
class ChoiceContentModel(ContentModel):
    """Represents a choice content model."""

    def __str__(self):
        return " | ".join(str(e) for e in self.elements)

@dataclass 
class Declaration:
    name:str
    keyword:str
    params:list[Any]
    open_delimiter:str = "<!"
    close_delimiter:str = ">"

    def __str__(self):
        params = " ".join(str(p) for p in self.params)
        return f"{self.open_delimiter}{self.keyword} {self.name} {params}{self.close_delimiter}"

@dataclass
class ElementDefinition(Declaration):
    content:ContentModel = EmptyContentModel
    tag_ommission_rules:str = ""

    def __init__(self, name, tag_omission_rules, content, *args):
        super().__init__(name=name, keyword="ELEMENT", params=(tag_omission_rules,content))
        self.content = content
        self.tag_omission_rules = tag_omission_rules

class LiteralStringValue:
    def __init__(self, components=None):
        """
        Initialize the LiteralStringValue with an optional list of components.
        
        Each component may be:
          - A string literal
          - An object that can be converted to a string
          - A callable returning a string
          
        By storing them as-is, we preserve their original form.
        """
        self._components = components[:] if components else []
        
    def append(self, component):
        """
        Add a new component to the list of elements.
        """
        self._components.append(component)
        
    def to_string(self):
        """
        Convert all components to a string. If any component is callable, call it.
        If it's not already a string, use `str()` to coerce it.
        """
        result_parts = []
        for comp in self._components:
            part = str(comp)
            result_parts.append(part)
        return "".join(result_parts)
    
    def get_components(self):
        """
        Return the original components for inspection.
        """
        return self._components[:]
        
    def __str__(self):
        """
        For convenience, when the object is converted to a string, return `to_string()`.
        """
        return f"\"" + self.to_string() + "\""

@dataclass
class EntityDefinition(Declaration):
    keyword = "ENTITY"
    parameter: bool = False
    value:List[Any] = None
#    content_model: ContentModel = None  # Reuse ContentModel for entity content
   
    def __init__(self, name, *args, parameter=False):
        super().__init__(name=name, keyword="ENTITY", params=(*args,))
        self.parameter = parameter

    def __str__(self):
        """Generates the SGML declaration string."""
        param_prefix = "%" if self.parameter else ""
        self.name = param_prefix + " " + self.name
        return super().__str__()

    def evaluate(self, registry: EntityRegistry) -> str:
        """
        Evaluates the entity by resolving any parameter references.
        :param registry: The registry to resolve parameter entities.
        :return: The fully expanded content of the entity.
        """
        evaluated_elements = []
        for el in self.elements:
            if el.startswith("%") and el.endswith(";"):
                # Extract parameter name
                param_name = el[1:-1]  # Strip `%` and `;`
                resolved_value = registry.resolve(param_name)
                if resolved_value is None:
                    raise ValueError(f"Parameter '{el}' is not defined in the registry.")
                evaluated_elements.append(resolved_value)
            else:
                # Literal value
                evaluated_elements.append(el)
        return " | ".join(evaluated_elements)

from __future__ import annotations  # Enable forward references
from typing import Any, Callable, Union, Dict, List, Optional
from dataclasses import dataclass

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

    def __contains__(self, item):
        """
        Check if the item exists in the components list.
        """
        return item in self._components

    def __iter__(self):
        """Iterate over components and recursively iterate through nested iterables."""
        for component in self._components:
            if hasattr(component, "__iter__") and not isinstance(component, str):
                # Recursively iterate over nested iterables
                yield from component
            else:
                yield component

    def __eq__(self, other):
        for comp in self._components:
            result = comp.__eq__(other)
            if result:
                return True
        return False
       
    def __str__(self):
        """
        For convenience, when the object is converted to a string, return `to_string()`.
        """
        return f"\"" + self.to_string() + "\""

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

class Parameter:
    def __init__(self, name: str, value: str):
        self._param_name = name
        self._param_value = value
    
    def __str__(self):
        return f"%{self._param_name};"

    def param_name(self) -> str:
        return self._param_name

    def param_value(self):
        return self._param_value

@dataclass 
class Declaration:
    keyword:str
    params:list[Any]
    name:Union[str, EntityDefinition] = ""
    open_delimiter:str = "<!"
    close_delimiter:str = ">"

    @property
    def name(self) -> str:
        """Intercept access to the `name` property."""
        if isinstance(self._name, EntityDefinition):
            if self._name.is_parameter():
                return self._name.param_value()
        return self._name

    @name.setter
    def name(self, value: Union[str, EntityDefinition]):
        """Allow setting the `name` property."""
        self._name = value
   
    def __str__(self):
        name = str(self._name)
        params = " ".join(str(p) for p in self.params)
        # Convert name to string or evaluate if it's a ContentModel
#        if isinstance(self.name, ContentModel):
#            name_str = f"(l{str(self.name)})"
#        elif isinstance(self.name, str) and self.name.startswith("%") and self.name.endswith(";"):
            # Ensure parameter entities are properly referenced
#            name_str = f"({str(self.name)})"
#        else:
#            name_str = self.name  # Raw string names
        return f"{self.open_delimiter}{self.keyword} {name} {params}{self.close_delimiter}"

@dataclass
class EntityDefinition(Declaration):
    keyword = "ENTITY"
    parameter: bool = False
    value:any = None
     
    def __init__(self, name, value, *args, parameter=False):
        super().__init__(name=name, keyword="ENTITY", params=(value, *args))
        self.parameter = parameter
        self.value = value

    def is_parameter(self) -> bool:
        """Check if this instance behaves as a Parameter."""
        return self.parameter

    def param_name(self) -> str:
        """Return the name of the parameter if it's acting as one."""
        if not self.is_parameter():
            raise AttributeError("This EntityDefinition is not a parameter.")
        return self.name

    def param_value(self) -> Any:
        """Return the value of the parameter if it's acting as one."""
        if not self.is_parameter():
            raise AttributeError("This EntityDefinition is not a parameter.")
        return self.value

    def __str__(self):
        string = super().__str__()
        if self.parameter:
            index = len(self.keyword) + string.find(self.keyword)
            return (string[:index] + " %" + string[index:])
        return string

   
class EntityRegistry:
    """Manages registration and lookup of parameter entities."""
    def __init__(self):
        self.registry: Dict[str, EntityDefinition] = {}

    def register(self, name: str, value: EntityDefinition):
        """Register a parameter entity with a name and value."""
        self.registry[name] = value

    def resolve(self, name: str) -> Optional[str]:
        """Resolve a parameter entity by name."""
        return self.registry.get(name)


@dataclass
class ContentModel:
    """Represents a generic content model."""
    elements: List[Union[str, "ContentModel", "RepetitionControl"]]
    group_repetition: Optional[RepetitionControl] = None  # Repetition applied to the group

    def _wrap_with_parentheses(self, content: str) -> str:
        """Ensure content is wrapped in parentheses."""
        return f"({content})"

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
        """Evaluate the content model by resolving parameter entities."""
        def resolve_element(el):
            if isinstance(el, str) and el.startswith("%") and el.endswith(";"):
                param_name = el[1:-1]
                resolved_value = registry.resolve(param_name) or el
                # Wrap resolved entities in parentheses if they represent choices or groups
                if "|" in resolved_value or "," in resolved_value:
                    return self._wrap_with_parentheses(resolved_value)
                return resolved_value
            return str(el)

        elements_str = " ".join(resolve_element(e) for e in self.elements)
        return self._wrap_with_repetition(elements_str)

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
    elements: List[Union[str, "RepetitionControl"]] 
    
    def __iter__(self):
        return iter(self.elements)

    def __str__(self):
        return "|".join(str(e) for e in self.elements)

@dataclass
class ElementDefinition(Declaration):

    content:ContentModel = EmptyContentModel
    tag_ommission_rules:str = ""

    def __init__(self, name, tag_omission_rules, content, *args):
        super().__init__(name=name, keyword="ELEMENT", params=(tag_omission_rules,content,args))
        self.content = content
        self.tag_omission_rules = tag_omission_rules
        self._name = name


from typing import Dict, Optional
from blog_improved.themes.base.theme import Theme, WidthNegotiator

class BaseTheme(Theme):
    def __init__(self, name=None, grid_config=None, width_scale=None, width_negotiator=None):
        self._name = name if name else "Base Theme"
        self._grid_config = grid_config if grid_config else { "container": "container", "column": "col", "row": "row", }
       
        self._width_scale = width_scale if width_scale else { 25: "one-quarter", 33: "one-third", 50: "one-half", 66: "two-thirds", 75: "three-quarters", 100: "full"}
        self._width_negotiator = width_negotiator if width_negotiator else WidthNegotiator(max_offset_percent=20)
        self._styles: Dict[str, str] = {}
        self._elements: Dict[str, str] = {}

    def get_element_attributes(self, element_name: str) -> Optional[Dict[str, str]]:
        """
        Returns the initial attributes for a given element.

        :param element_name: The HTML element name (e.g., "a", "div").
        :return: A dictionary of attributes or None if not defined.
        """
        return self._elements.get(element_name, {})

    def apply_theme(self, theme):
        self._name = theme.get("name")
        self._styles = theme.get("styles")
        self._elements = theme.get("elements")

    def get_column_class(self, size):
        """Returns the appropriate class for a given column size."""
        column_str = self._grid_config.get("column", "")
        width_str = find_width(size)
        width_str = "-" + width_str if width_str else ""  
        return column_str + width_str

    def find_width(self, value):
        """
        Find the nearest width class for a given value, with negotiation for out-of-range values.

        :param value: The input size value.
        :return: The matching width class or None.
        """
        if not isinstance(value, (int, float, complex)):
            raise ValueError("Expected a number type")

        # Adjust value if it's beyond the highest scale
        min_value = min(self._width_scale.keys()) 
        max_value = max(self._width_scale.keys())
        negotiated_value = self._width_negotiator.negotiate(value, min_value, max_value)

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

    def resolve_grid_class(self, role, size):
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

        width_str = self.find_width(size)
        if not width_str:
            raise ValueError(f"Invalid size: {size}")
        return f"{self._grid_config[role]}-{width_str}"

from typing import Dict, Optional
from blog_improved.themes.base.theme import Theme

class BaseTheme(Theme):
    def __init__(self, name=None, grid_config=None, width_scale=None):
        self._name = name if name else "Base Theme"
        self._grid_properties = grid_config if grid_config else { "container": "container", "column": "col", "row": "row", } 
        self._width_scale = width_scale if width_scale else { 25: "3", 33: "4", 50: "6", 66: "8", 75: "9", 100: "12"}
        self._styles: Dict[str, str] = {}
        self._elements: Dict[str, str] = {}

    def get_element_attributes(self, element_name: str) -> Optional[Dict[str, str]]:
        """
        Returns the initial attributes for a given element.

        :param element_name: The HTML element name (e.g., "a", "div").
        :return: A dictionary of attributes or None if not defined.
        """
        return self._elements.get(element_name, {})

    def get_styles(self):
        return self._styles

    def apply_theme(self, theme):
        self._name = theme.get("name")
        self._styles = theme.get("styles")
        self._elements = theme.get("elements")
   
    @property
    def width_scale(self):
        return self._width_scale
    
    @property
    def grid_properties(self):
        return self._grid_properties


import re
from typing import Dict, Optional
from ..serializers import TOMLSerializer
from blog_improved.themes.base.theme import Theme

class BaseTheme(Theme):
    def __init__(self, name=None, version=None, authors=None, source_license=None, variant=None, media=None, grid_config=None, width_scale=None, serializer=TOMLSerializer()):
        self.name:str = name if name else "Base Theme"
        self.version:str = version
        self.authors:list[str] = authors
        self.license:str = source_license
        self.variant = variant
        self.media:list[str] = []
        self._serializer = serializer
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

    def save_to_file(self, filepath):
        attributes = dict()
        for attr_name in dir(self):
            if (not re.match("^(_.|__.)", attr_name) and 
                not callable(getattr(self, attr_name))):
                value = getattr(self, attr_name)
                if attr_name == "width_scale": 
                    value = {str(k): v for k, v in value.items()}
                attributes[attr_name] = value
  
        serialized_data = self._serializer.serialize(attributes)

        with open(filepath, "w") as f:
            f.write(serialized_data)

    def get_styles(self):
        return self.styles

    def apply_theme(self, theme, styles):
        self.name = theme.get("name")
        self.styles = styles.get("style_mappings")
        self.elements = styles.get("elements")
   
    @property
    def width_scale(self):
        return self._width_scale
    
    @property
    def grid_properties(self):
        return self._grid_properties


from .presentation_strategy import PresentationStrategy, Rect
from blog_improved.formatters.html.html_generator import SgmlComponent

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


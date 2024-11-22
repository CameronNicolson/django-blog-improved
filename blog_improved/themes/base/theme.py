from enum import Enum
from abc import ABC, abstractmethod

class THEME_DEFAULT_FONT(Enum):
		# For static text, edit boxes, lists and most other places
		ETDF_DEFAULT = 0,
		# Font for buttons
		ETDF_BUTTON = 1,
		# Font for window title bars
		ETDF_WINDOW = 2,
		# Font for menu items
		ETDF_MENU = 3,
		# Font for tooltips
		ETDF_TOOLTIP = 4,
		# this value is not used, it only specifies the amount of default fonts available.
		ETDF_COUNT = 5

ThemeFontNames = [
		"defaultFont",
		"buttonFont",
		"windowFont",
		"menuFont",
		"tooltipFont",
		None
	]

class WidthNegotiator:
    def __init__(self, max_offset_percent=20):
        """
        Initialize the negotiator with an allowed offset percentage.

        :param max_offset_percent: The maximum allowable offset as a percentage.
        """
        self.max_offset_percent = max_offset_percent

    def negotiate(self, value, min_value, max_value):
        """
        Negotiate a value against the maximum allowed value.

        :param value: The input value to evaluate.
        :param max_value: The maximum allowable value.
        :return: Adjusted value if within the offset range, otherwise None.
        """
        min_limit = min_value - (max_value * self.max_offset_percent / 100) 
        max_limit = max_value + (max_value * self.max_offset_percent / 100)
        if value <= min_value and value >= min_limit:
            return min_value
        elif value > min_value and value <= max_limit:
            return min(value, max_value)
        return None

class Theme(ABC):
    @abstractmethod
    def resolve_grid_class(self, size):
        pass


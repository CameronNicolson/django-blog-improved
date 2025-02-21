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

class Theme(ABC):
    def get_styles():
        raise NotImplemented()

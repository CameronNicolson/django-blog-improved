from blog_improved.themes.base.base_theme import BaseTheme
from blog_improved.conf import get_theme_settings

# Globals to hold the theme instance
_theme_instance = None

def get_theme():
    """
    Lazily initializes and returns the global theme instance.
    """
    global _theme_instance

    if _theme_instance is None:  # Initialize if not already done
        theme_name = get_theme_settings()
        # TODO: Handle alternative themes
        if theme_name.lower() == "fallback":
            _theme_instance = BaseTheme()
        else:
            # If alternative themes are implemented later
            raise ValueError(f"Unknown theme: {theme_name}")
    else:
        _theme_instance = BaseTheme()
    return _theme_instance

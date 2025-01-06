from pathlib import Path
from blog_improved.themes.base.base_theme import BaseTheme

# Globals to hold the theme instance
_theme_instance = None

def compute_sha(n):
    return None

def load_theme(theme_path: Path):
    sha = "placeholder"
    current_sha = compute_sha(theme_path)

    if current_sha is None:
        print("Config file not found. Using default theme settings.")
        theme = get_theme()
        theme.apply_theme({"name": "Base Theme", "styles": {"article__title": "fs-5 fw-bold", "article__headline": "fs-6 lh-sm", "article__title-link": "link-dark link-opacity-75-hover link-underline-opacity-50-hover", "article__category-link": "link-secondary link-underline-opacity-25"}, "elements": {"h2": {"class": None}, "p": {"class": None}, "a": {"class": "link link-offset-3 link-opacity-50-hover"}}})
    elif sha != current_sha:
        print("Config file has changed. Loading new settings.")
        sha = current_sha
    else:
        print("Config file unchanged. Using cached theme settings.")


def get_theme():
    """
    Lazily initializes and returns the global theme instance.
    """
    global _theme_instance

    if _theme_instance is None:  # Initialize if not already done
        theme_name = "fallback"
        # TODO: Handle alternative themes
        if theme_name.lower() == "fallback":
            _theme_instance = BaseTheme()
        else:
            # If alternative themes are implemented later
            _theme_instance = BaseTheme()
    return _theme_instance


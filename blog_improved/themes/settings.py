from __future__ import annotations
from pathlib import Path
from blog_improved.themes.base.base_theme import BaseTheme
from blog_improved.io.data_directory_manager import DataDirectoryManager

# Globals to hold the theme instance
_theme_instance = None

def compute_sha(n):
    return None

ThemeConfig = dict[str, str]

def load_theme_config(theme_path: Path, serializer:Serializer):
    config = None

    if theme_path.is_file() == False:
        raise ValueError("File not found")
    
    config = serializer.deserialize(theme_path)
    return config

def find_theme(theme_name:str, filename:str, paths:list[Path], serializer:Serializer) -> ThemeConfig:

    if theme_name == "":
        raise ValueError("You did not provide a theme name") 
    if filename == "":
        raise ValueError("You did not provide a filename.") 
    if paths == None:
        raise ValueError("The list of paths to look for a theme cannot be empty.") 

    for path in paths:
        theme_config_path = path / filename
        if not theme_config_path.is_file():
            continue
        config = load_theme_config(theme_config_path, serializer)
        if str(config["name"]).lower() == str(theme_name).lower():
            return config

    raise FileNotFoundError(f"No theme found: failure when searching for \"name = {theme_name}\" in {paths.__str__()}")

def load_theme(theme_path: Path):
    sha = "placeholder"
    current_sha = compute_sha(theme_path)
    if current_sha is None:
        print("Config file not found. Using default theme settings.")
        theme = get_theme()
        theme.apply_theme({"name": "Base Theme"}, {"style_mappings": {"article__title": "fs-5 fw-bold", "article__headline": "fs-6 lh-sm", "article__title-link": "link-dark link-opacity-75-hover link-underline-opacity-50-hover", "article__category--link": "link-secondary link-underline-opacity-25", "list": "list-unstyled"}, "elements": {"h2": {"class": None}, "p": {"class": None}, "ul": {"class": None}, "a": {"class": "link link-offset-3 link-opacity-50-hover"}}})
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


from django.conf import settings

LAYOUT_POSTLIST = getattr(settings, "BLOG_LAYOUT_POSTLIST", None)

USER_PUBLIC_PROFILE = getattr(settings, "BLOG_USER_PUBLIC_PROFILE", True)
AUTHOR_DEFAULT_GROUP = getattr(settings, "BLOG_AUTHOR_DEFAULT_GROUP", "author")
HOMEPAGE_LATESTPOSTS_SIZE = getattr(settings, "BLOG_HOMEPAGE_LATESTPOSTS_SIZE", 6)  

FALLBACK_THEME = "fallback"

def get_theme_settings():
    theme = getattr(settings, "BLOG_THEME", FALLBACK_THEME)
    return theme

def set_dynamic_settings(settings):
    """
    Call this func at the end of the project's settings file.
    It takes settings module globals dict for updating with some 
    final tweaks for settings that generally aren't specified, 
    but can be given some better defaults based on other settings 
    that have been specified.
    """

    blog_dependencies = [
        "redirects",
        "crispy_forms",
        "crispy_forms_gds",
        "phonenumber_field",
        "taggit",
        "blog_improved",
    ]

    for app in blog_dependencies:
        if app not in settings["INSTALLED_APPS"]:
            try:
                __import__(app)
            except ImportError:
                pass
            else:
                settings["INSTALLED_APPS"].append(app)

#####################
# FORMATTER SETTINGS
#####################
_env_settings = {}

def set_env_settings(settings_dict):  # Function to populate settings
    global _env_settings
    _env_settings.update(settings_dict)  # Merge with existing settings

def get_env_setting(setting_name):
    return _env_settings.get(setting_name)


FORMATTER_OPTIONS = getattr(settings, "BLOG_FORMATTER", {})

SGML_GENERATOR = FORMATTER_OPTIONS.get("sgml_generator", "html")
PRESENTATION_STRATEGY = FORMATTER_OPTIONS.get("presentation_strategy", "inline")
LAYOUT_PRESETS = FORMATTER_OPTIONS.get("layout_presets", "fallback")

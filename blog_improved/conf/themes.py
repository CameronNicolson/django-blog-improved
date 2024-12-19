FALLBACK_THEME = "fallback"

def get_theme_settings():
    theme = getattr(settings, "BLOG_THEME", FALLBACK_THEME)
    return theme

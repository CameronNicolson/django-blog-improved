from django.conf import settings

def api_user_config_activated():
    setting = getattr(settings, "BLOG_IMPROVED_API_ACTIVATED", None)
    if setting is True:
        return True
    else:
        return False

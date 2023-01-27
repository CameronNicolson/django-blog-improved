from django.conf import settings

USER_PUBLIC_PROFILE = getattr(settings, "BLOG_USER_PUBLIC_PROFILE", True)
AUTHOR_DEFAULT_GROUP = getattr(settings, "BLOG_AUTHOR_DEFAULT_GROUP", "author")

def set_dynamic_settings(settings):
    """
    Call this func at the end of the project's settings file.
    It takes settings module globals dict for updating with some 
    final tweaks for settings that generally aren't specified, 
    but can be given some better defaults based on other settings 
    that have been specified.
    """

    print(settings)
    try:
        settings["INSTALLED_APPS"]
    except ValueError:
        pass
    else:
        print("hello HELLO \n \n")
        print(settings["INSTALLED_APPS"])

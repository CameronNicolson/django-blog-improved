from django.conf import settings

USER_PUBLIC_PROFILE = getattr(settings, "BLOG_USER_PUBLIC_PROFILE", True)
AUTHOR_DEFAULT_GROUP = getattr(settings, "BLOG_AUTHOR_DEFAULT_GROUP", "author")
HOMEPAGE_LATESTPOSTS_SIZE = getattr(settings, "BLOG_HOMEPAGE_LATESTPOSTS_SIZE", 6)  


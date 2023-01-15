from django.conf import settings

USER_PUBLIC_PROFILE = getattr(settings, 'BLOG_USER_PUBLIC_PROFILE', True)

from functools import wraps
from blog_improved.models import Status
from blog_improved.authors.models import cast_user_to_postauthor
from blog_improved.conf import USER_PUBLIC_PROFILE as profiles_enabled

# Define privacy settings that can be toggled
privacy_settings = {
    "show_real_name": profiles_enabled
}

from functools import wraps
from blog_improved.models import Status
from blog_improved.conf import USER_PUBLIC_PROFILE as is_profiles_enabled

# Privacy settings: If profiles are enabled, cloaking should be False (show real names)
privacy_settings = {
    "show_real_name": is_profiles_enabled
}

def author_privacy(func):
    """
    Decorator to handle author privacy settings.
    Allows an override to manually disable or enable name cloaking when needed.
    """
    @wraps(func)
    def wrapper(post, cloak_override=None):
        """
        If `cloak_override` is provided, use that setting.
        Otherwise, follow the privacy setting (show_real_name).
        """
        cloak_name = not privacy_settings["show_real_name"]  # If showing real names, then cloaking should be False
        if cloak_override is not None:
            cloak_name = cloak_override  # Override if explicitly provided
        return func(post, cloak_name)

    return wrapper

@author_privacy
def get_author_details(post, cloak_name):
    """Extract and process author details for a given post."""
    author = None
    author_name = None
    author_profile = None
    author_url = None

    if post.author:
        author = cast_user_to_postauthor(post.author)
        author_profile = getattr(post.author, "userprofile", None)

    if author_profile:
        # Use provided cloak_name value (which may be overridden by decorator)
        cloak_name = author_profile.status == Status.PRIVATE.value if cloak_name is None else cloak_name
        author_url = author_profile.url
    else:
        # No profile exists so cloak name
        cloak_name = cloak_name if cloak_name else True

    if author:
        author_name = author.get_display_name(cloak_name)

    return author_name, author_url


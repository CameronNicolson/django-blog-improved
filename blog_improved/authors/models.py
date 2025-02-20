import copy
from django.db.models import (Model,
        CASCADE,
        CharField,
        ForeignKey,
        IntegerField,
        OneToOneField,
        SET_NULL,
        URLField,
        TextField
)

from django.contrib.auth.models import User
from blog_improved.models import Media, Status
from blog_improved.conf import is_public_profile_active

is_profile_active = is_public_profile_active

def user_profile_choice_code(public_status=is_profile_active):
    if public_status:
        return Status.PUBLISH.value
    return Status.PRIVATE.value

class PostAuthor(User):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_display_name(self, cloak):
        """Returns the appropriate display name based on the cloak setting."""
        if not cloak and self.get_full_name():
            return self.get_full_name()
        return self.username

class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    bio = TextField(max_length=500, blank=True)
    location = CharField(max_length=30, blank=True)
    url = URLField(blank=True)

    avatar = ForeignKey(Media, on_delete=SET_NULL, blank=True, null=True)

    status = IntegerField(
        choices=Status.choices, 
        default=user_profile_choice_code() 
        )

    def __str__(self):
        return "UserProfile {0}".format(self.user.username).title()

def cast_user_to_postauthor(user: User) -> PostAuthor:
    """Returns a User instance casted as PostAuthor with proper initialization."""
    if not isinstance(user, User):
        raise ValueError("Provided instance is not a User")

    user_copy = copy.copy(user)  # Avoid mutating the original
    user_copy.__class__ = PostAuthor  # Change the class

    return user_copy

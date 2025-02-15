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
    return Status.Private.value

class PostAuthor(User):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cloak_identity = True

    def cloak_identity(self, active):
        """Sets the temporary cloak identity flag."""
        self._cloak_identity = active  # Temporarily store in instance memory

    def get_display_name(self):
        """Returns the appropriate display name based on the cloak setting."""
        if not self._cloak_identity and self.get_full_name():
            return self.get_full_name()
        return self.username

class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    bio = TextField(max_length=500, blank=True)
    location = CharField(max_length=30, blank=True)
    website = URLField(blank=True)

    avatar = ForeignKey(Media, on_delete=SET_NULL, blank=True, null=True)

    status = IntegerField(
        choices=Status.choices, 
        default=user_profile_choice_code() 
        )

    def __str__(self):
        return "UserProfile {0}".format(self.user.username).title()


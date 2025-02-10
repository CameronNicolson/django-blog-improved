from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import Tag
from blog_improved.conf import USER_PUBLIC_PROFILE
from django.db.models.signals import pre_save, post_save, pre_init
from django.dispatch import receiver

from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

class Status(models.IntegerChoices):
    DRAFT = 0
    PUBLISH = 1
    PRIVATE = 2
    UNLISTED = 3

    @classmethod
    def name_to_id(cls, name):
        if not isinstance(name, str):
            raise TypeError("Argument 'name' must be a string")
        if not name:
            raise ValueError("Argument 'name' cannot be an empty string")

        for choice in cls:
            if choice.name == name.upper():
                return choice.value
        raise ValueError(f"Unknown status with name '{name}'")
 

def user_profile_choice_code(public_status):
    if public_status:
        return 1
    return 2

def set_upload_directory(instance, filename):
    updir = "" # upload directory string
    match instance.mediatype:
        case Media.MediaType.AUDIO:
            updir += "/audio/"
        case Media.MediaType.VIDEO:
            updir += "/vid/"
        case Media.MediaType.IMAGE:
            updir += "/img/"
        case Media.MediaType.DOCUMENT:
            updir += "/documents/"
        case _:
            updir += "/"
    return "{0}/{1}".format(updir, filename)

 
class BlogGroup(Group):
    status = models.IntegerField(choices=Status.choices, default=Status.PRIVATE) 

    class Meta: 
        verbose_name_plural = "groups"


class Media(models.Model):
    class MediaType(models.TextChoices):
        AUDIO = "AUD"
        VIDEO = "VID"
        IMAGE = "IMG"
        DOCUMENT = "DOC"

    title = models.TextField(max_length=250, blank=True)
    file = models.FileField(blank=True)
    mediatype = models.CharField(max_length=3, choices=MediaType.choices)
    upload_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta: 
        verbose_name_plural = "media"

    def __str__(self):
        return "Media {} {}".format(self.mediatype, self.title)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)

    avatar = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True)

    status = models.IntegerField(
        choices=Status.choices, 
        default=user_profile_choice_code(
                USER_PUBLIC_PROFILE
            ) 
        )

    def __str__(self):
        return "{0} Intimate Details".format(self.user.username).title()

class TagGroup(models.Model):
    tags = TaggableManager()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        new_profile = UserProfile.objects.create(user=instance)
        new_profile.save()

class Contact(models.Model):
    name = models.CharField(max_length=200, blank=False)
    notes = models.TextField(blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    # Below are the mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

class EmailAddress(models.Model):
    contact = GenericRelation("Contact")
    email_address = models.EmailField() 

    def getAddressAsString(self):
        return str(self.email_address)

class SiteSettings(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    default_contacts = models.ForeignKey(
            "Contact", on_delete=models.CASCADE, null=True, blank=True)


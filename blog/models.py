from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from blog.conf import USER_PUBLIC_PROFILE
from taggit.managers import TaggableManager
from taggit.models import Tag
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save, post_save, pre_init
from django.dispatch import receiver
from model_utils.managers import InheritanceManager
from model_utils.models import StatusModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

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

class Status(models.IntegerChoices):
    DRAFT = 0
    PUBLISH = 1
    PRIVATE = 2
    UNLISTED = 3

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

class TaggedPost(TaggedItemBase):
    content_object = models.ForeignKey('Post', on_delete=models.CASCADE)

class Post(models.Model):
    objects = InheritanceManager()
    
    status = models.IntegerField(
        choices=Status.choices, 
        default=Status.DRAFT
    )

    class CollabrationMode(models.IntegerChoices):
        NO = 0, ('No')
        YES = 1, ('Yes')

        __empty__ = ('(Unknown)')

    collabaration_mode = models.IntegerField(
        choices=CollabrationMode.choices,
        default=CollabrationMode.NO,
    )

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    is_featured = models.BooleanField(default=False, db_column="featured")
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    headline = models.CharField(max_length=200, blank=True)
    cover_art = models.ForeignKey(
        Media, on_delete=models.SET_NULL, blank=True, null=True
    )
    category = models.ForeignKey(Tag, db_column="category", related_name="categories", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(through=TaggedPost)

    class Meta:
        ordering = ("-created_on",)

    def __str__(self):
        return self.title
    
    def get_post_type(self):
        return self._meta.model_name

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": str(self.slug)})

class PostViaGit(Post):
    associated_git_repository = models.URLField()

    def save(self, *args, **kwargs):
        if self.collabaration_mode == Post.CollabrationMode.__empty__:
            raise ValueError("Posts using Git require collabration to be turned on")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Posts with Git"

    def __str__(self):
        return self.title

class PostRedirect(Post):
    redirect_url = models.URLField()

    def get_absolute_url(self):
        return self.redirect_url


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_on",)

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)


class Callback(models.Model):
    receipt_name = models.CharField(max_length=255)
    telephone_number = PhoneNumberField(blank=False)
    note = models.TextField(max_length=500)

@receiver(post_save, sender=Post)
def upgrade_to_collab_mode(sender, instance, *args, **kwargs):
        # Make Post into PostViaGit when Collab is on
        if instance.collabaration_mode == 1:
            try:
                PostViaGit.objects.get(post_ptr_id=instance.id)
            except ObjectDoesNotExist:
                instance = PostViaGit(post_ptr=instance)
                instance.save_base(raw=True)

@receiver(post_save, sender=PostViaGit)
def remove_collab_mode(sender, instance, created, *args, **kwargs):
    if created:
        return 

    if instance.collabaration_mode == Post.CollabrationMode.NO:
        instance.delete(keep_parents=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        new_profile = UserProfile.objects.create(user=instance)
        new_profile.save()

@receiver(pre_save, sender=PostRedirect)
def update_postredirect_slug(sender, instance, **kwargs):
    instance.slug = "{0}s-redirect".format(slugify(instance.title))
    return instance

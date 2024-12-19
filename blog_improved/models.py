from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from blog_improved.conf.models import USER_PUBLIC_PROFILE, AUTHOR_DEFAULT_GROUP
from taggit.managers import TaggableManager
from taggit.models import Tag
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save, post_save, pre_init
from django.dispatch import receiver
from model_utils.managers import InheritanceManager
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


class PublicStatusManager(InheritanceManager):

    def include_status(self, status):
        status_list = [Status.PUBLISH]
        status_list.append(status)
        return self.get_queryset(status_list)
        
    def include_unlisted(self):
        return self.include_status(Status.UNLISTED)

    def get_queryset(self, status=[Status.PUBLISH]):
        return super().get_queryset().filter(status__in=status)


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
    # Custom Managers 
    public = PublicStatusManager()
    published_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-published_on",)

    def __str__(self):
        return self.title
   

    def save(self, *args, **kwargs):
        if self.pk is None:  # This is a new post being created
            if self.status == 1:  # Only set publication date if status is 1
                self.publication_date = timezone.now()
        else:  # This is an existing post being updated
            post_before_save = Post.objects.get(pk=self.pk)
            if original_post.status not in [1, self.status] and self.status == 1:
                self.publication_date = timezone.now()
        
        super().save(*args, **kwargs)

    def get_post_type(self):
        return self._meta.model_name

    def get_author_url(self):
        isAuthor = User.objects.filter(pk=self.author.id, groups__name=AUTHOR_DEFAULT_GROUP).exists()
        if isAuthor:
            return reverse("user_profile", kwargs={"group": str(AUTHOR_DEFAULT_GROUP), "name": str(self.author.username)})
        return None

    
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

class PostShoutout(Post):
    redirect_url = models.URLField()

    class Meta:
        verbose_name_plural = "Post Shoutouts"

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

@receiver(pre_save, sender=PostShoutout)
def update_postredirect_slug(sender, instance, **kwargs):
    instance.slug = "{0}s-shoutout".format(slugify(instance.title))
    return instance

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


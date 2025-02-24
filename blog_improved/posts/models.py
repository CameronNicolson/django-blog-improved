from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    DateTimeField, 
    ForeignKey,
    IntegerChoices, 
    IntegerField, 
    Model,
    SET_NULL,
    URLField,
    SlugField,
    TextField
)
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.urls import reverse
from blog_improved.conf import USER_PUBLIC_PROFILE, AUTHOR_DEFAULT_GROUP
from blog_improved.db.managers import PublicStatusManager
from taggit.managers import TaggableManager
from taggit.models import Tag
from model_utils.managers import InheritanceManager
from blog_improved.models import Media, Status
from taggit.models import TaggedItemBase

def get_default_category():
    instance, _ = Tag.objects.get_or_create(name="uncategorised")
    return instance.id

class TaggedPost(TaggedItemBase):
    content_object = ForeignKey("Post", on_delete=CASCADE)

class Post(Model):
    objects = InheritanceManager()
    
    status = IntegerField(
        choices=Status.choices, 
        default=Status.DRAFT
    )

    title = CharField(max_length=200, unique=True)
    slug = SlugField(max_length=200, unique=True, blank=False)
    author = ForeignKey(
        User, on_delete=CASCADE, related_name="blog_posts"
    )
    is_featured = BooleanField(default=False, db_column="featured")
    updated_on = DateTimeField(auto_now=True)
    content = TextField()
    headline = CharField(max_length=200, blank=True)
    cover_art = ForeignKey(
        Media, on_delete=SET_NULL, blank=True, null=True
    )
    category = ForeignKey(Tag, db_column="category", related_name="categories", on_delete=CASCADE, default=get_default_category)
    created_on = DateTimeField(auto_now_add=True)
    tags = TaggableManager(through=TaggedPost)
    # Custom Managers 
    public = PublicStatusManager()
    published_on = DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-published_on",)

    def __str__(self):
        return self.title
   
    def save(self, *args, **kwargs):
        self.slug = self.slug if self.slug else slugify(self.title) 
 
        if self.pk is None:  # This is a new post being created
           if self.status == 1:  # Only set publication date if status is 1
                self.publication_date = timezone.now()
        else:  # This is an existing post being updated
            post_before_save = Post.objects.get(pk=self.pk)
            if post_before_save.status not in [Status.PUBLISH.value, self.status] and self.status == Status.PUBLISH.value: # post is being published so needs a publish date
                self.publication_date = timezone.now()
        
        super().save(*args, **kwargs)

    def get_post_type(self):
        return self._meta.model_name

    def get_author_url(self, author_group=AUTHOR_DEFAULT_GROUP):
        isAuthor = User.objects.filter(pk=self.author.id, groups__name=author_group).exists()
        if isAuthor:
            return reverse("user_profile", kwargs={"group": str(AUTHOR_DEFAULT_GROUP), "name": str(self.author.username)})
        return None

    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": str(self.slug)})

class PostShoutout(Post):
    redirect_url = URLField()

    class Meta:
        verbose_name_plural = "Post Shoutouts"

    def get_absolute_url(self):
        return self.redirect_url

@receiver(pre_save, sender=PostShoutout)
def update_postredirect_slug(sender, instance, **kwargs):
    instance.slug = "{0}s-shoutout".format(slugify(instance.title))
    return instance


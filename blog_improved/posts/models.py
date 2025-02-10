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

class TaggedPost(TaggedItemBase):
    content_object = ForeignKey("Post", on_delete=CASCADE)

class Post(Model):
    objects = InheritanceManager()
    
    status = IntegerField(
        choices=Status.choices, 
        default=Status.DRAFT
    )

    class CollabrationMode(IntegerChoices):
        NO = 0, ('No')
        YES = 1, ('Yes')

        __empty__ = ('(Unknown)')

    collabaration_mode = IntegerField(
        choices=CollabrationMode.choices,
        default=CollabrationMode.NO,
    )

    title = CharField(max_length=200, unique=True)
    slug = SlugField(max_length=200, unique=True)
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
    category = ForeignKey(Tag, db_column="category", related_name="categories", on_delete=CASCADE)
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

    def get_author_url(self, author_group=AUTHOR_DEFAULT_GROUP):
        isAuthor = User.objects.filter(pk=self.author.id, groups__name=author_group).exists()
        if isAuthor:
            return reverse("user_profile", kwargs={"group": str(AUTHOR_DEFAULT_GROUP), "name": str(self.author.username)})
        return None

    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": str(self.slug)})

class PostViaGit(Post):
    associated_git_repository = URLField()

    def save(self, *args, **kwargs):
        if self.collabaration_mode == Post.CollabrationMode.__empty__:
            raise ValueError("Posts using Git require collabration to be turned on")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Posts with Git"

    def __str__(self):
        return self.title

class PostShoutout(Post):
    redirect_url = URLField()

    class Meta:
        verbose_name_plural = "Post Shoutouts"

    def get_absolute_url(self):
        return self.redirect_url

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

@receiver(pre_save, sender=PostShoutout)
def update_postredirect_slug(sender, instance, **kwargs):
    instance.slug = "{0}s-shoutout".format(slugify(instance.title))
    return instance



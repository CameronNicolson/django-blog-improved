from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from django.utils.html import format_html
from .models import Comment, BlogGroup, Post, PostViaGit, PostShoutout, Media, TagGroup, UserProfile
from taggit.models import Tag
from django.db.models import Prefetch
from redirects.models import Redirect
from redirects.admin import RedirectAdmin

@admin.register(Post)
class PostAdmin(admin.ModelAdmin): 
    list_display = ("title", "slug", "status", "created_on", "content",)
    add_form_template = False
    change_form_template = "blog_improved/admin/post_changeform.html"

    list_display = ("title", "slug", "status", "created_on", "content",)
    list_filter = ("status", "created_on")
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    fields = ("title", "slug", "headline", "content", "author", "category", "tags", "status", "is_featured", "cover_art", "collabaration_mode",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tags(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    
    def add_view(self, request, extra_context=None):
        return super(PostAdmin, self).add_view(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        post_slug = Post.objects.get(pk=object_id).slug
        paths = [post_slug, "/" + post_slug, "/" + post_slug + "/"]
        extra_context.update({
            "post_full_url": request.build_absolute_uri(Post.objects.get(pk=object_id).get_absolute_url()),
            "redirects": Redirect.objects.filter(new_path__in=paths),
        })
        return super(PostAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_changeform_initial_data(self, request):
        return {'author': request.user}

@admin.register(PostViaGit)
class PostGitAdmin(PostAdmin):
    fields = ("title", "slug", "headline", "content", "author", "category", "tags", "status", "is_featured", "cover_art", "collabaration_mode", "associated_git_repository")
    list_display = ("title",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")


@admin.register(PostShoutout)
class PostShoutoutAdmin(PostAdmin):
    fields = ("title", "headline", "content", "author", "category", "status", "is_featured", "cover_art", "redirect_url")
    prepopulated_fields = {} 


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "body", "post", "created_on", "active")
    list_filter = ("active", "created_on")
    search_fields = ("name", "email", "body")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    pass

@admin.register(TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

admin.site.unregister(Site)
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [UserProfileAdmin,]

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "domain")
    list_display_links = ("id", 'name',)
    readonly_fields = ("id",)

@admin.register(BlogGroup)
class BlogGroupAdmin(admin.ModelAdmin):
    list_display = ("name","status",)

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    pass

from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site

from .models import Comment, BlogGroup, Post, PostViaGit, PostRedirect, Media, TagGroup, UserProfile
from taggit.models import Tag

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ("title", "slug", "status", "created_on", "tags")
    list_filter = ("status", "created_on")
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    summernote_fields = ("content",)
    fields = ("title", "slug", "headline", "content", "author", "category", "tags", "status", "is_featured", "cover_art", "collabaration_mode")
   
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tags(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def get_changeform_initial_data(self, request):
        return {'author': request.user}

@admin.register(PostViaGit)
class PostGitAdmin(PostAdmin):
    fields = ("title", "slug", "headline", "content", "author", "category", "tags", "status", "is_featured", "cover_art", "collabaration_mode", "associated_git_repository")
    list_display = ("title",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")


@admin.register(PostRedirect)
class PostRedirectAdmin(PostAdmin):
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


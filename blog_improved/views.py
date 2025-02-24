from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.http import Http404
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.contrib.auth.models import User
from blog_improved.conf import HOMEPAGE_LATESTPOSTS_SIZE as latest_post_limit
from blog_improved.posts.models import Post, PostShoutout
from blog_improved.models import BlogGroup, Status
from blog_improved.authors.models import UserProfile
from taggit.models import Tag
from django.db.models.base import ModelBase
from django.db.models import Q, QuerySet
from model_utils.managers import InheritanceManager, InheritanceManagerMixin
from itertools import chain
from blog_improved.constants import BLOG_POST_CONTEXT_NAME

import operator

def page_not_found(request, exception):
    context = {}
    response = render(request, "pages/errors/404.html", context=context)
    response.status_code = 404
    return response

def filter_classes(queryset, model_list):
    filtered_list = []
    for obj in queryset:
        for model in model_list:
            if not isinstance(obj, model):
                filtered_list.append(obj)
    return filtered_list

def list_to_queryset(model, data):

    if not isinstance(model, ModelBase):
        raise ValueError(
            "%s must be Model" % model
        )
    if not isinstance(data, list):
        raise ValueError(
            "%s must be List Object" % data
        )

    pk_list = [obj.pk for obj in data]
    return model.objects.filter(pk__in=pk_list)

# ========== Mixins ==========

class AccessStatusMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # Get the object whose status you want to check
        obj = self.get_object()
        if obj:
        # Check the status
            if obj.status == Status.PUBLISH or obj.status == Status.UNLISTED:
                # Status is public or unlisted, continue with the view
                return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404

class BaseUrlMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = "{0}://{1}{2}".format(self.request.scheme, self.request.get_host(), self.request.path)
        return context

# ========== Class Views ==========

class HomePage(BaseUrlMixin, InheritanceManagerMixin, ListView):
    template_name = "blog_improved/pages/homepage.html"
    featured_post_limit = 1

    def get_queryset(self, *args, **kwargs):
        # live posts sorted by created date and public status
        live = Post.public.all().order_by('-published_on')[:latest_post_limit]
        # posts with feature state
        featured = Post.public.filter(is_featured=True).order_by('-published_on')[:self.featured_post_limit]

        # convert querytsets to lists is a workaround
        # for collecting subclasses of Post
        live_objects = list(live)
        featured_objects = list(featured)

        combined_queryset = Post.objects.all().filter(
            pk__in=set(obj.pk for obj in chain(live_objects, featured_objects))
        ).select_subclasses()

        return combined_queryset

class AuthorPage(ListView):
    author_template_dir = "blog_improved/pages/authors/"
    model = BlogGroup

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_object_or_404(qs, name__contains=self.kwargs["group"])
        names_in_url = self.kwargs["name"].split(',')
        qs = qs.user_set.all()
        qs = qs.filter(username__in=names_in_url)
        qs = get_list_or_404(UserProfile, user__in=qs, status=1)
        return qs

    def get_template_names(self):
        return [ self.author_template_dir + self.kwargs["name"] + ".html".lower(), 
                "blog_improved/pages/author.html", 
        ]        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) or {}
        names_in_url = self.kwargs["name"].split(',')

        if len(self.get_queryset()) < len(names_in_url):
            raise Http404

        users = get_list_or_404(User, username__in=names_in_url)

        def create_user_list(lista, listb):
            for user, profile in zip(lista, listb):
                user.username = user.username.capitalize()
                yield from ((user, profile,),)

        context["profile"] = list(create_user_list(users, self.get_queryset()))
        context["group"] = BlogGroup.objects.get(name=self.kwargs["group"])
        return context

class PostView(DetailView, AccessStatusMixin, SingleObjectMixin):
    template_name = "blog_improved/single_post.html"
    model = Post

    def get_object(self, queryset=None):
        # Get the object using the manager and apply additional filtering
        obj = None
        try:
            lookup = self.kwargs.get("slug", None)
            if lookup:
                obj = Post.public.include_unlisted().get(slug=lookup)
        except Post.DoesNotExist:
            raise Http404
        return obj
    
    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        post = self.get_object()
        context[BLOG_POST_CONTEXT_NAME] = post
        return context


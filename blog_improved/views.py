from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.http import Http404
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogGroup, Post, PostViaGit, PostRedirect, UserProfile, Status
from .forms import FilterForm
from taggit.models import Tag
from django.db.models.base import ModelBase
from django.db.models import Q, QuerySet
from itertools import chain

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

class PublicStatusMixin(object):
    target_status = [Status.PUBLISH]

    def get_queryset(self):
        qs = super().get_queryset()
        status_ids = self.target_status
        return qs.filter(status__in=status_ids)

class HomePage(ListView):
    template_name="blog_improved/pages/homepage.html"
    queryset = Post.objects.filter(status=1).select_subclasses()

    class Meta:
        ordering = ["-created_on"]

class AuthorPage(PublicStatusMixin, ListView):
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


class PostList(ListView):
    paginate_by = 10
    
    def post(self, request, *args, **kwargs):
        # category tags passed by POST request
        form = FilterForm(request.POST)
        if form.is_valid():
            cat_list = form.cleaned_data["category"]
            cats = get_list_or_404(Tag.objects.filter(pk__in=cat_list))
            cat_list_str = str()
            for i in range(len(cat_list)):
                cat_list_str += cats[i].name
                if i+1 < len(cat_list):
                    cat_list_str += ","
            return redirect(f"/search?cat={cat_list_str}")
        return render(request, "blog_improved/post_list.html", {"filter_form": form})

    def get(self, request, *args, **kwargs):
        # categories in request string, seperated by comma
        req_cats = self.request.GET.get("cat") or None
        if req_cats is not None:
            self.request.categories = req_cats.split(",")  
        else:
            self.request.categories = []
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # show all posts for index pages
        if "/index/" in self.request.path:
            all_posts = Post.objects.filter(status=1).select_subclasses(PostRedirect)
            posts_cleaned = filter_classes(all_posts, (PostRedirect,))
            return list_to_queryset(Post, posts_cleaned)
        try:
            # remove whitespaces enteries
            cats = [cat for cat in self.request.categories if cat != ""]
            # only filter by category if string parameters are detected
            if len(cats) > 0:
                # get posts with a matching category
                all_posts = Post.objects.filter(status=1, category__name__in=cats).select_subclasses(PostRedirect)
                # here we are removing PostRedirect from posts list
                posts_cleaned = filter_classes(all_posts, (PostRedirect,))
                # build new queryset with list above
                return list_to_queryset(Post, posts_cleaned)
            return Post.objects.none()
        except AttributeError:
            raise Http404
        return Post.objects.none()
        

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        # Find all tags that were inside the request
        categories = self.request.categories
        if len(categories) > 0:
            cat_ids = []
            for cat_name in categories:
                cat_ids.append(str(Tag.objects.get(name=cat_name).pk))
            # pass all found tags to the FilterForm
            context["filter_form"] = FilterForm(initial={"category": cat_ids})
        else: 
            context["filter_form"] = FilterForm()
        context["total_post_count"] = self.get_queryset().count()
        context["search_title"] = "Posts"
        try: 
            context["filter_categories"] = self.request.categories
            # send query context for the Next/Prev pagination
            context["query"] = self.request.GET.get("cat")
        except KeyError:
            return context
        return context


class PostView(DetailView, PublicStatusMixin, SingleObjectMixin):
    template_name = "blog_improved/post_detail.html"
    model = Post
    target_status = [Status.PUBLISH, Status.UNLISTED]

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        post = self.get_object()
        context["crumbs"] = [("Home", reverse("home"),),("Posts", reverse("post_list"),),(post.title, None,)]
        
        if operator.eq(post.collabaration_mode, Post.CollabrationMode.YES):
            post = get_object_or_404(PostViaGit, post_ptr_id=post.pk)
        context["post"] = post
        return context


import sys 
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.template import TemplateSyntaxError
from classytags.core import Tag, Options
from classytags.arguments import Argument, KeywordArgument
from classytags.values import ChoiceValue, DictValue, ListValue, StringValue, StrictStringValue, IntegerValue
from classytags.utils import TemplateConstant
from blog_improved.vendor.classytags.arguments import CommaSeperatableMultiKeywordArgument 
from blog_improved.vendor.classytags.values import DateTimeValue
from blog_improved.posts.posts import PostListQueryRequest, PostListQueryService
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.posts.post_list_markup_presets import create_post_list_markup, layout_presets
from blog_improved.posts.models import Post as post_model
from blog_improved.models import Status
from blog_improved.formatters.env import get_env
from blog_improved.authors.models import cast_user_to_postauthor, PostAuthor
from blog_improved.posts.posts import Post
from blog_improved.utils.normalise import normalise_post_entry

class PostTag(Tag):
    name = "post"
    post_model = post_model

    options = Options(
                KeywordArgument("post_id", resolve=False, required=False),    
            )

    def __init__(self, parser, tokens):
        super().__init__(parser, tokens)
    
    @property
    def model(self):
        return self.post_model

    def render(self, context):
        post_context = context.get("post", {})
        post = normalise_post_entry(post_context) 
        context["post"] = post or {}
        # Determine if a post is present and return if found
        if post and post.title:
            self.kwargs["pre_fetched"] = IntegerValue(TemplateConstant(1))
            self.kwargs["slug"] = StringValue(TemplateConstant(post.slug))
            self.kwargs["post_id"] = TemplateConstant(None)
            self.kwargs["lookup"] = DictValue({})
            return super().render(context)

        id_value = self.kwargs.get("post_id", {}).setdefault("id", TemplateConstant(None))
        slug_value = StringValue(TemplateConstant(post_context.get("slug", None)))
        self.kwargs["slug"] = slug_value 
        lookup_key, lookup_value = None, None
        if id_value.resolve(context):
            lookup_key, lookup_value = ("id", IntegerValue(id_value))
        elif slug_value.resolve(context):
            lookup_key, lookup_value = ("slug", StringValue(slug_value))
        else:
            raise TemplateSyntaxError(
                f"{sys.modules[__name__].__name__} {self.__class__.__name__}: Neither id nor slug was provided."
            )
        
        if lookup_value == "":
            raise TemplateSyntaxError(
                f"{sys.modules[__name__].__name__} {self.__class__.__name__}: {lookup_key}'s value \"{lookup_value}\" is malformed or missing."
            )
 
        lookup = DictValue({lookup_key: lookup_value}) if lookup_value else TemplateConstant(None)

        # Store values in options and proceed
        self.kwargs["lookup"] = lookup
        self.kwargs["pre_fetched"] = IntegerValue(TemplateConstant(0))          # Explicitly mark as not pre-fetched
        return super().render(context)

    def render_tag(self, context, lookup, pre_fetched, post_id, slug):
        markup = get_env().blog_factory
        post = None

        if lookup is None and pre_fetched is False:
            return ""

        if pre_fetched:
            post = context.get("post")
        else:
            try:
                post = self.model.objects.select_related("author__userprofile").get(**lookup)
            except ObjectDoesNotExist:
                raise TemplateSyntaxError(
                    f"{sys.modules[__name__].__name__} {self.__class__.__name__}: No matching records found for {self.model} lookup '{lookup}'."
                 )
        try:
            cloak_name = True
            author_profile = False
            if post.author:
                author_profile = getattr(post.author, "userprofile", None)
            if author_profile:
                cloak_name = True if author_profile.status == Status.PRIVATE.value else False

            author = cast_user_to_postauthor(post.author)
            html = markup.create_article(
                title=post.title,
                headline=post.headline,
                author=author.get_display_name(cloak_name),
                author_homepage=False,
                date=post.published_on,
                body_content=post.content,
                category=post.category,
                featured=post.is_featured,
                article_url=None,
                content=post.content
        )
            return html.render()
        except KeyError as error:
            if hasattr(error, 'message'):
                return TemplateSyntaxError(error.message)
            else:
                raise error
        return ""

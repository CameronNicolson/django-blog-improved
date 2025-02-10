from django.apps import apps
from django.template import TemplateSyntaxError
from classytags.core import Tag, Options
from classytags.arguments import Argument
from classytags.values import ChoiceValue, ListValue, StringValue, IntegerValue
from classytags.utils import TemplateConstant
from blog_improved.vendor.classytags.arguments import CommaSeperatableMultiKeywordArgument 
from blog_improved.vendor.classytags.values import DateTimeValue
from blog_improved.posts.posts import PostListQueryRequest, PostListQueryService
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.helpers.html_generator import BlogHtmlFactory, HtmlGenerator, create_blog_html_factory
from blog_improved.posts.post_list_markup_presets import create_post_list_markup, layout_presets
from blog_improved.posts.models import Post as post_model

HTML_FACTORY_INSTANCE = create_blog_html_factory()

class PostTag(Tag):
    name = "post"
    post_model = post_model

    options = Options()

    def __init__(self, parser, tokens):
        super().__init__(parser, tokens)
    
    @property
    def model(self):
        return self.post_model

    def render(self, context):
        options = {}
        slug = context.get("post", {}).get("slug", None)
        if slug:
            slug = TemplateConstant(slug)
        else:
            slug = StringValue(TemplateConstant(""))

        options["slug"] = slug
        self.kwargs = options
        return super().render(context)

    def render_tag(self, context, slug):
        post = None
        if slug:

            post = self.model.objects.filter(slug=slug)
        if post:
            return "we found you"

        return "didnt find"

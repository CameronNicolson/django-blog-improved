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

# Access the AppConfig instance
config = apps.get_app_config("blog_improved")

HTML_FACTORY_INSTANCE = create_blog_html_factory()

class PostlistTag(Tag):
    name = "postlist"
    service_filters = PostListQueryService() 

    options = Options(
            CommaSeperatableMultiKeywordArgument("postlist_options", resolve=False, required=False, delimiter=",", commakwargs=["category", "ignore_category"]),
        "as",
        Argument("varname", required=False, resolve=False)
    )

    def __init__(self, parser, tokens):
        super().__init__(parser, tokens)
    
    @property
    def _sort_choice(self):
        ChoiceValue.choices = ["asc", "desc"]
        return ChoiceValue

    @property
    def _format_layout_choice(self):
        ChoiceValue.choices = ["grid", "list"]
        return ChoiceValue

    def _get_layout(self, name): 
        layout = None
        try: 
            layout = layout_presets[name]
        except KeyError:
            raise TemplateSyntaxError(f"The provided layout {name} is not a registered layout.")
        return layout 

    def render(self, context):
        try:
            options = self.kwargs.pop("%s_options" % self.name) 
            options.setdefault("custom_filter", TemplateConstant(""))
            options.setdefault("layout_format", TemplateConstant("grid"))
            options.setdefault("layout", TemplateConstant("default"))
            options.setdefault("varname", TemplateConstant(False))
            options.setdefault("date_range", TemplateConstant("9999-12-31 23:59:59.999999"))
            options.setdefault("max_count", TemplateConstant("-1"))
            # empty strings in max_count will be counted as "-1"
            if not bool(str(options["max_count"].resolve(None))):
                options["max_count"] = TemplateConstant("-1")
            options.setdefault("featured_count", TemplateConstant("-1"))
            options.setdefault("category", ListValue(TemplateConstant("all")))
            options.setdefault("ignore_category", TemplateConstant(""))
            options.setdefault("name", TemplateConstant(self.name))
            options.setdefault("featured", TemplateConstant(False))

            options.setdefault("sort", TemplateConstant("model"))

            options["date_range"] = DateTimeValue(options["date_range"])
            options["max_count"] = IntegerValue(options["max_count"]) 

            options["featured_count"] = IntegerValue(options["featured_count"]) 
            options["name"] = StringValue(options["name"])

            variable_name = self.kwargs.get("varname", TemplateConstant(False)) 
            options["varname"] = variable_name

            try:
                self._sort_choice(options["sort"])
                self._format_layout_choice(options["layout_format"])
            except TemplateSyntaxError: 
                options["sort"] = None
            self.kwargs = options
        except Exception as e:
            raise TemplateSyntaxError(str(e))
        finally:
            return super().render(context)

    def render_tag(self, context, name, max_count, featured_count, category, featured, ignore_category, date_range, sort, layout, layout_format, custom_filter, varname=None):
        layout = self._get_layout(layout)
        posts = PostListQueryRequest()
        if max_count < 0:
            max_count = layout.rows * layout.columns
        if custom_filter:
            posts = self.service_filters("custom_filter", posts)
        else:
            posts.max_size(max_count)\
                    .categories(category)\
                    .date_range(date_range)\
                    .sort(sort)\
                    .ignored(tuple(("category__name", "exact", ic,) for ic in ignore_category))\
                    .featured(featured, featured_count)\
                    .status(1)\
                    .return_type("values_list")
        if max_count > 0:        
            posts = posts.build()
        else: 
            posts = []
        markup = create_post_list_markup(name, posts, 
                                         layout, 
                                         HTML_FACTORY_INSTANCE)
        markup.build_grid()
        markup.generate_html(layout_type=layout_format)
        html = markup.get_rendered()
        if varname:
            context[varname] = html
            return ""
        return html


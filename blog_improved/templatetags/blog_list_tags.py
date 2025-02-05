import warnings
from datetime import datetime
from django.conf import settings
from django import template
from django.template import Context, Template
from django.template import Node, TemplateSyntaxError
from django.db.models.query import QuerySet
from django.db.models import Q
from blog_improved.models import Post, Status
from blog_improved.utils.strings import split_string, convert_str_kwargs_to_list
from blog_improved.query_request.query import QueryRequest, FilterQueryRequest
from classytags.core import Tag, Options
from classytags.values import ChoiceValue, StrictStringValue, StringValue, ListValue, DictValue
from classytags.arguments import MultiKeywordArgument as ClassyTagsMultiKeywordArgument
from classytags.arguments import Argument, KeywordArgument, StringArgument, MultiValueArgument
from classytags.values import IntegerValue
from classytags.utils import TemplateConstant
from django.template.base import Variable, VariableDoesNotExist
from blog_improved.posts.posts import PostListQueryRequest
from blog_improved.posts.post_list_markup import PostListMarkup
from blog_improved.helpers.html_generator import BlogHtmlFactory, HtmlGenerator, create_blog_html_factory
from blog_improved.posts.post_list_markup_presets import create_post_list_markup, POST_LIST_GRID_PRESETS
from django.apps import apps

# Access the AppConfig instance
config = apps.get_app_config("blog_improved")

HTML_FACTORY_INSTANCE = create_blog_html_factory()

register = template.Library()

bloglist_args_mapping = {
    "category": {
        "FilterQueryRequest": {
            "negate": False,
            "lookup_field": "category",
            "lookup_type": "exact",
            "lookup_value": None
        }
    },
    "ignore-category": {
        "FilterQueryRequest": {
            "negate": True,
            "lookup_field": "category",
            "lookup_type": "exact",
            "lookup_value": None
        }
    },
    "visibility": {
        "FilterQueryRequest": {
            "negate": False,
            "lookup_field": "status",
            "lookup_type": "exact",
            "lookup_value": None
        }
    }

}

decorator_registry = {
        "FilterQueryRequest": FilterQueryRequest
}

def apply_sequence_queryset_request(instance: QueryRequest, requests_to_apply:list):
    queryset_request = instance
    for request in requests_to_apply:
        for classname, class_kwargs in request.items():
            class_ref = decorator_registry.get(classname)
            if class_ref:
                decorator = class_ref(queryset_request=queryset_request, **class_kwargs)
                queryset_request = decorator
    return queryset_request

def translate_kwargs(tag_kwargs):
    translated_kwargs = []
    for tag_key, tag_value in tag_kwargs.items():
        list_classes = bloglist_args_mapping.get(tag_key) or iter([])
        for class_key, class_vals in list_classes.items():
            new_kwargs = dict((k, tag_value) if None else (k, v) for k, v in class_vals.items() ) 
            translated_kwargs.append({class_key: new_kwargs})
    return translated_kwargs

class MultiKeywordArgument(ClassyTagsMultiKeywordArgument):
  #  sequence_class = ListValue
    def __init__(self, name, default=None, required=True, resolve=True,
                 defaultkey=None, splitter='=', commakwarg=None):
        super().__init__(name, default, required, resolve, defaultkey, splitter)
        self.commakwarg = commakwarg

    def parse_token(self, parser, token):
         # Call the parent method to get the token parsed as usual
        options = super().parse_token(parser, token)
        key, value = options

        # Check if the key is in the list that requires comma-splitting
        if key in self.commakwarg:
            if isinstance(value, StringValue):
                # Split the resolved value and handle the empty case
                resolved_value = value.resolve(None)
                if resolved_value:  # Only proceed if resolved_value is not empty or None
                    list_values = [TemplateConstant(item) for item in resolved_value.split(',')]
                    # Initialize the ListValue with the first item, if any
                    template_list = ListValue(list_values[0]) if list_values else ListValue()
                    # Append remaining values, if any
                    template_list.extend(list_values[1:])
                    # Update options with the new ListValue
                    options = (key, template_list)
        return options

class DictWithListValue(dict, StringValue):
    def __init__(self, value):
        new_dict = value
        for key, string in value.items():
            new_dict[key] = list()
            for s in split_string(string.literal):
                new_dict[key].append(s)
#            for split_str in split_string(string.literal):
            #new_dict[key].append(split_str)
        dict.__init__(self, new_dict)

    def clean(self, value):
        return value

    def resolve(self, context):
        resolved = {}
        for key, value in self.items():
            for list_val in value:
                try:
                    resolved_value = Variable(list_val) 
                    resolved_value = resolved_value.resolve(context)
                except VariableDoesNotExist:
                    resolved_value = None  # or handle the error as needed
                resolved[key] = resolved_value
        return self.clean(resolved)

from django.utils.dateparse import parse_datetime

class DateTimeValue:
    errors = {
        'invalid': "Invalid datetime value: %(value)s",
    }
    value_on_error = None

    def __init__(self, var):
        self.var = var
        try:
            self.literal = self.var.literal
        except AttributeError:
            self.literal = self.var.token

    def resolve(self, context):
        resolved = self.var.resolve(context)
        return self.clean(resolved)

    def clean(self, value):
        if isinstance(value, datetime):
            return value  # Already a datetime object
        
        if isinstance(value, str):
            parsed = parse_datetime(value)
            if parsed is not None:
                return parsed
            
        return self.error(value, 'invalid')

    def error(self, value, category):
        data = self.get_extra_error_data()
        data['value'] = repr(value)
        message = self.errors.get(category, "") % data
        
        if settings.DEBUG:
            raise template.TemplateSyntaxError(message)
        else:
            # warnings.warn(message, template.TemplateSyntaxError)
            return self.value_on_error

    def get_extra_error_data(self):
        return {}

ChoiceValue.choices.extend(["asc", "desc"])

class BlogListTag(Tag):
    name = "bloglist"
    options = Options(
        MultiKeywordArgument("bloglist_options", resolve=False, required=False, commakwarg=["category", "ignore_category"]),
        "as",
        Argument("varname", required=False, resolve=False)
    )

    def __init__(self, parser, tokens):
        super().__init__(parser, tokens)
    
    def render(self, context):
        try:
            options = self.kwargs.pop("%s_options" % self.name) 

            options.setdefault("varname", TemplateConstant(False))
            options.setdefault("date_range", TemplateConstant("9999-12-31 23:59:59.999999"))
            options.setdefault("max_count", TemplateConstant("-1"))
            # empty strings in max_count will be counted as "-1"
            if not bool(str(options["max_count"].resolve(None))):
                options["max_count"] = TemplateConstant("-1")
            options.setdefault("featured_count", TemplateConstant("-1"))
            options.setdefault("category", ListValue(TemplateConstant("all")))
            options.setdefault("ignore_category", TemplateConstant(""))
            options.setdefault("name", TemplateConstant("bloglist"))
            options.setdefault("featured", TemplateConstant(False))

            options.setdefault("sort", TemplateConstant(""))

            options["date_range"] = DateTimeValue(options["date_range"])
            options["max_count"] = IntegerValue(options["max_count"]) 

            options["featured_count"] = IntegerValue(options["featured_count"]) 
            options["name"] = StringValue(options["name"])

            variable_name = self.kwargs.get("varname", TemplateConstant(False)) 
            options["varname"] = variable_name

            try:
                ChoiceValue(options["sort"]) 
            except TemplateSyntaxError: 
                options["sort"] = None
            self.kwargs = options
        except:
            pass
        finally:
            return super().render(context)

    def render_tag(self, context, name, max_count, featured_count, category, featured, ignore_category, date_range, sort, varname=None):
        layout_name = "standard_3by3"
        if max_count < 0:
            layout = POST_LIST_GRID_PRESETS[layout_name]
            max_count = layout["rows"] * layout["columns"]

        posts = PostListQueryRequest()\
                    .max_size(max_count)\
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
            print("it was zero")
            posts = []
        markup = create_post_list_markup(name, posts, 
                                         layout_name, 
                                         HTML_FACTORY_INSTANCE)
        markup.build_grid()
        markup.generate_html(layout_type="row")
        html = markup.get_rendered()
        print(html)
        if varname:
            print(varname)
            context[varname] = html
            return ""
        return html


def bloglist(parser, token):
    # add visibility if not provided by tag
    if kwargs.get("visibility") == None:
        kwargs["visibility"] = Status.name_to_id("publish")
    for key, arg in kwargs.items():
        BlogListTagParams(key, arg)
    # OK we have came to the decision to use the register.tag() the parser
    # make the kwarg into function pointer and its args


    requests = translate_kwargs(kwargs)
    initial_request = QueryRequest("blog_improved", "Post", [])
    bob = apply_sequence_queryset_request(initial_request, requests) 
    return {} 

def querysetfilter(func):
    """
    Decorator for filters which should only receive querysets. The object
    passed as the first positional argument will be type checked.
    """
    def _dec(first, *args, **kwargs):
        if isinstance(first, QuerySet) and not isinstance(first, EmptyQuerySet):
            result = func(first, *args, **kwargs)
        return result

    return _dec

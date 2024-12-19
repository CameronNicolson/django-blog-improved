import re, copy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django import template 
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from blog_improved.models import Contact, Post, Status, SiteSettings
from blog_improved.conf.models import HOMEPAGE_LATESTPOSTS_SIZE as default_limit
from blog_improved.utils.urls import starts_with_uri, URLBuilder
from django.db.models.query import QuerySet
from model_utils.managers import InheritanceQuerySet
from blog_improved.templatetags.blog_list_tags import BlogListTag, bloglist

DEFAULT_POST_STATUS = "PUBLISH"

register = template.Library()

register.tag(BlogListTag)

@register.simple_tag(takes_context=True)
def url_gen(context, subpath="", baseUrl="", trailing_slash=True):
    """
    Generate a complete URL by combining the base URL from context and a provided slug.

    This template tag takes the incoming context and an optional `slug`. Outputs are 
    different based on the case provided:
    1. If subpath is missing, return None.
    2. If subpath starts with a URI then return None.
    3. If baseUrl is available, it concatenates baseUrl and subpath.
    4. If both baseUrl is empty, it returns None.

    Args:
        context (dict): The context dictionary containing variables accessible in the template.
        slug (str, optional): A string to be appended to the base URL. Defaults to None.

    Raises:
        template.VariableDoesNotExist: If `subpath` is not provided.

    Returns:
        str: The complete URL.

    Notes:
        The `starts_with_uri` function is used to determine if `subpath` starts with a URI.

    Example:
        {% url_gen subpath='/music/bands/neworder/' %}
    """
 
    if not subpath:
        raise template.VariableDoesNotExist(f"{url_gen.__name__} template tag's parameter `subpath` cannot be empty") 
    
   # subpaths with uri such as http(s), do not require the website's base url 
    if starts_with_uri(subpath):
        return None

    if baseUrl == "":
        base_url = context.get("base_url", None)
   
    if base_url:
        url = URLBuilder(base_url)
        # foreach item in the subpath then add to url builder
        # exclude empty strings from subpath list
        for item in subpath.split("/"): 
            if item != "":
                url.add_subpath(item)
        if trailing_slash:
            url.add_endslash()

        full_url = url.build()
        return full_url
    else:
        return None

@register.simple_tag 
def total_post_count(status_type=DEFAULT_POST_STATUS):
    """
    Retrieves the total count of posts with a specified status type.

    This template tag fetches the count of posts with a given status type.
    The status type is provided as a string, which is then converted to its corresponding
    integer ID using the 'name_to_id' method of the 'Status' enumeration.

    Args:
        status_type (str, optional): The status type to filter the posts. Defaults to DEFAULT_POST_STATUS.

    Returns:
        int: The total count of posts with the specified status.

    Raises:
        template.TemplateSyntaxError: If there is a syntax error in the template.
        template.VariableDoesNotExist: If the provided status type is not a valid status.

    Example Usage:
        {% total_post_count "DRAFT" %}
        This will return the count of posts with the status "DRAFT".
    """

    status = {}
    try:
        choice = Status.name_to_id(status_type) 
    except TypeError as e:
        raise template.TemplateSyntaxError(e)
    except ValueError as e:
        raise template.VariableDoesNotExist(f"Value '{status_type}' provided to {total_post_count.__name__} is not a status") 
    status = {'status': choice}
    return Post.objects.filter(**status).count()

def filter_posts(queryset, size=default_limit, allow_featured=True):
    if isinstance(queryset, QuerySet) or isinstance(queryset, InheritanceQuerySet):
        if queryset.model is Post:
            pure_list = []
            for value in queryset:
                if size and len(pure_list) >= size:
                    break
                if value.is_featured is allow_featured:
                    pure_list.append(value)
            return pure_list
    return []

@register.filter
def regular(queryset, size=None):
    return filter_posts(queryset, size=size, allow_featured=False)

@register.filter
def featured(queryset, size=None):
    return filter_posts(queryset, size=size, allow_featured=True)

@register.simple_tag(takes_context=True)
def contact_list(context, **kwargs):
    contact_list = list()
    services = kwargs
    for service in services:
        try:
            contact = {}
            contact_link = contact_us(context, choice=service)
            if(contact_link):
                contact["uri"] = contact_link
                contact["method_name"] = str(service).capitalize() 
                contact_list.append(contact)
        except KeyError:
            contact = None
    return contact_list


@register.simple_tag(takes_context=True)
def contact_us(context, choice="", url="", mailto="", using_site=True, **kwargs):
    choices_as_names = {"email": "emailaddress"}
    mailto_css = "govuk-link govuk-link--no-visited-state"
    curr_site = get_current_site(context["request"])
    if kwargs:
        try:
            url = kwargs["url"] is True
        except KeyError:
            url = "" 
        for key,value in choices_as_names.items():   
            if key in kwargs:
                contact = kwargs[key]
    if choice:
        try:
            settings = SiteSettings.objects.get(site=curr_site)
            contact = settings.default_contacts
            if settings == None:
                raise ObjectDoesNotExist
            try:
                related_type = choices_as_names[choice]
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist
            content_type_queryset = ContentType.objects.get(app_label="blog_improved", model=related_type)
            relation = content_type_queryset.get_object_for_this_type(contact=contact) or None
            contact = relation.getAddressAsString()
            if not relation:
                raise ObjectDoesNotExist
        except (KeyError, ObjectDoesNotExist) as e:
            return None
    if url or mailto:
        if not choice:
            contact = url or mailto
        return obfuscate_mailto(contact, mail=mailto, text=contact, css_class=mailto_css)
    return obfuscate(contact)

@register.inclusion_tag("blog_improved/partials/main-nav.html", takes_context=True)
def main_nav(context):
    navigation = {}
    current_url = {}
    try: 
        navigation, current_url = context["navigation"], context["current_url"]
    except KeyError:
        pass

    return {"pages": navigation, "request_url_name": current_url}

def obfuscate_string(value):
    return ''.join(['&#{0:s};'.format(str(ord(char))) for char in value])

@register.filter
@stringfilter
def obfuscate(value):
    return mark_safe(obfuscate_string(value))

@register.filter
@stringfilter
def obfuscate_mailto(value, mail=False, text=False, css_class=False):
    if mail:
        url = "{0:s}{1:s}".format(obfuscate_string('mailto:'), obfuscate_string(value))
    else:
        url = "{0:s}".format(obfuscate_string(value))
    if text:
        link_text = text
        # Detect subject lines
        if ';' in text:
            args = text.split(';')
            link_text = args[0]
            subject = args[1]
            mail = mail + '?subject=' + subject
    else:
        link_text = mail
    return mark_safe('<a class="{2:s}" href="{0:s}">{1:s}</a>'.format(
        url, link_text, css_class))

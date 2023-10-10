import re, copy
from django.conf import settings
from django import template 
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

from ..models import Post, Status 

from django.db.models.query import QuerySet
from model_utils.managers import InheritanceQuerySet

DEFAULT_POST_STATUS = "PUBLISH"

@register.simple_tag(takes_context=True)
def url_gen(context, slug=None):
    """
    Generate a complete URL by combining the base URL from context and a provided slug.

    This template tag takes the incoming context and an optional `slug`. Outputs are 
    different based on the case provided:
    1. If baseUrl and slug are both not empty, it concatenates them.
    2. If baseUrl is empty and slug is provided, it returns slug.
    3. If both baseUrl and slug are empty, it raises a VariableDoesNotExist exception.

    Args:
        context (dict): The context dictionary containing variables accessible in the template.
        slug (str, optional): A string to be appended to the base URL. Defaults to None.

    Raises:
        template.VariableDoesNotExist: If `slug` is not provided.

    Returns:
        str: The complete URL.
    """

    view_base_url = context.get("base_url", None)
    baseUrl = view_base_url or slug
    if baseUrl and slug:
        return f"{baseUrl}{slug}"
    elif not baseUrl and slug:
        return slug
    else:
        raise template.VariableDoesNotExist(f"{url_gen.__name__} template tag's parameter `slug` cannot be empty") 

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

def filter_posts(queryset, size=6, allow_featured=True):
    if type(queryset) is QuerySet or type(queryset) is InheritanceQuerySet:
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


@register.simple_tag
def contact_us(choice=False, url=False, mailto=False, **kwargs):
    if choice == "":
        return None
    choices_as_names = {"email": "DEFAULT_EMAIL", "matrix": "MATRIX_ID"}
    mailto_css = "govuk-link govuk-link--no-visited-state"
    if kwargs:
        try:
            url = kwargs["url"] is True or kwargs["mailto"] is True
        except KeyError:
            url = False    
        for key,value in choices_as_names.items():   
            if key in kwargs:
                contact = kwargs[key]
    if choice:
        try:
            choice_keyword_in_settings = choices_as_names[choice]
            contact = settings.CONTACT[choice_keyword_in_settings]
        except AttributeError:
            contact = "please enter {0} in settings.py".format(choice)
    if url or mailto:
        return obfuscate_mailto(url, mail=mailto, text=contact, css_class=mailto_css)
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

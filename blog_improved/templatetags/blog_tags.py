import re, copy
from django.conf import settings
from django import template 
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

from ..models import Post 

from django.db.models.query import QuerySet
from model_utils.managers import InheritanceQuerySet

DEFAULT_POST_STATUS = "PUBLISH"

@register.simple_tag 
def total_post_count(status_choice=None):
    status = {}
    if status_choice:
        status = {'status': Post.Status[status_choice.upper()]}

    return Post.objects.filter(**status).count()

@register.filter
def featured(queryset, limit=6, invert=False):
    if type(queryset) is QuerySet or type(queryset) is InheritanceQuerySet:
        if queryset.model is Post:
            pure_list = []
            for value in queryset:
                if limit != None and len(pure_list) >= int(limit):
                    break
                if value.is_featured is not invert:
                    pure_list.append(value)
            return pure_list
    return

@register.filter
def not_featured(queryset, in_limit=None):
    return featured(queryset, limit=in_limit, invert=True)

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

@register.inclusion_tag("partials/main-nav.html", takes_context=True)
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

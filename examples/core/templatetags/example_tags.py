from django import template

register = template.Library()

@register.inclusion_tag("breadcrumbs.html")
def breadcrumbs(crumbs):
    """
    Inclusion tag that renders the HTML needed to display Breadcrumbs component.

    Examples::

        {% load example_tags %}
        ...
        {% breadcrumbs crumbs %}

    Args:
        crumbs: a list of 2-tuples. The tuple is made up of the link title followed
            by the link URL.

    """
    return {"crumbs": crumbs}

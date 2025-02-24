import copy, re, threading
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from blog_improved.utils.urls import prettify_url
from django.contrib.sites.shortcuts import get_current_site
thread_lock = threading.Lock()

def site(request):
    if apps.is_installed("django.contrib.sites"):
        Site = apps.get_model("sites.Site")
        try:
            current_site = get_current_site(request)
            return {"site": {"name": current_site.name, "domain": current_site.domain } }
        except Site.DoesNotExist:
            return ""

def get_navigation_links(pages):
    pages = pages or []
    def get_links():
        links = []
        for page in pages:
            nav_item = copy.copy(page)
            url = page["URL"]
            # if external service (outside of your domain e.g. ibm.com)
            is_external = re.findall(r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url)
            if is_external:
                nav_item["PATTERN_NAME"] = None
                links.append(nav_item)
                continue
            nav_item["PATTERN_NAME"] = url
            nav_item["URL"] = reverse(url)
            links.append(nav_item)
        return links
    return get_links

def get_pages():
    return []

def navigation(request):
    request_url_name = request.resolver_match.url_name
    with thread_lock:
        pages = get_pages()
        links = get_navigation_links(pages)
        navigation = cache.get_or_set('navigation', links)
    return {"navigation": navigation, "current_url": request_url_name}


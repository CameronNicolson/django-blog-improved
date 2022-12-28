import copy, re, threading
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from utils.prettify_url import *
from django.contrib.sites.shortcuts import get_current_site
thread_lock = threading.Lock()

def site(request):
    try:
        current_site = get_current_site(request)
        return {"site": {"name": current_site.name, "domain": current_site.domain } }
    except ObjectDoesNotExist:
        return ""

def get_pages(page_settings=settings.MAIN_NAVIGATION_PAGES):
    links = []
    for page in page_settings:
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

def get_crumbs(request):
    page_title = prettify_url(request.resolver_match.view_name)
    return [("Home", reverse("home"),),(page_title, None,)]

def navigation(request):
    request_url_name = request.resolver_match.url_name
    crumbs = get_crumbs(request)
    with thread_lock:
        navigation = cache.get_or_set('navigation', get_pages)
    return {"navigation": navigation, "current_url": request_url_name, "crumbs": crumbs }


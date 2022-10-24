import re

def prettify_url(url_name):
    url_name = re.compile('[^a-zA-Z]').sub(" ", url_name)
    url_name = url_name.capitalize()
    return url_name
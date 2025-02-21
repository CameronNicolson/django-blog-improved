from re import compile as re_compile 
from re import match

def prettify_url(url_name):
    url_name = re_compile('[^a-zA-Z]').sub(" ", url_name)
    url_name = url_name.capitalize()
    return url_name

def starts_with_uri(text):
    pattern = r"^\w+://"
    return match(pattern, text) is not None

class URLBuilder:
    """
    A class for constructing URLs by assembling base URL, subpaths, and end slash state.

    Usage:
    url_builder = URLBuilder(base_url)
    url_builder.add_subpath(subpath1).add_subpath(subpath2).add_endslash()
    full_url = url_builder.build()

    Args:
    base_url (str): The base URL of the resource.

    Attributes:
    base_url (str): The base URL of the resource.
    subpaths (list): A list of subpaths to be appended to the base URL.
    endslash (EndSlash): An instance of EndSlash used to manage the end slash state.

    Methods:
    add_subpath(subpath): Add a subpath to the URL.
    add_endslash(): Add a trailing slash to the URL.
    build(): Construct the final URL.
    """

    class EndSlash:
        """
        EndSlash:
        A class managing the end slash state.

        Methods:
        off(): Turn off the end slash.
        on(): Turn on the end slash.
        __str__(): Return a string representation of the end slash.
        __repr__(): Return a string representation of the end slash.

        Example:

        url_builder = URLBuilder("https://example.com")
        url_builder.add_subpath("path").add_endslash()
        full_url = url_builder.build()  # Result: "https://example.com/path/"

        """

        def __init__(self):
            self.state = False
        def off(self):
            self.state = False
        def on(self):
            self.state = True
        def __str__(self):
            return "/" if self.state else ""
        def __repr__(self):
            return "/" if self.state else ""
            
    def __init__(self, base_url):
        self.base_url = base_url
        self.subpaths = []
        self.endslash = self.EndSlash()
        self.endslash.off()

    def add_subpath(self, subpath):
        self.subpaths.append(subpath)
        return self

    def add_endslash(self):
        self.endslash.on()
        return self

    def build(self):
        full_url = self.base_url + '/'.join(self.subpaths) + str(self.endslash)
        return full_url


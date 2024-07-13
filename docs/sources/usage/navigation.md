# Navigation 

You can control what pages show up in the navigation menu by simply altering the list inside settings.

## Display navigations in HTML templates

To display, insert `{{ main_nav }}` where you want the main navigation to be accessed. 

## Change navigation appearance 

The template is stored in `partials/main_nav.html` within the blog templates folder. 

You are free to change the CSS classes and HTML elements to your liking. 

When done, refresh the server and it's cache should reveal your changes to the website. 
 
### Add a new link 

Head over to `config/settings.py`. Find the line within the document that says `MAIN_NAVIGATION_PAGES`, near the bottom. 

To add a new link, insert an additional element within the list.

```
# Before
MAIN_NAVIGATION_PAGES = [
    {"TITLE": "Contact", "URL": "contact"},
    {"TITLE": "Services", "URL": "services"},
    {"TITLE": "Projects", "URL": "projects"},
    {"TITLE": "About", "URL": "about"},
    {"TITLE": "External", "URL": "https://fsf.org"},
]

# After
MAIN_NAVIGATION_PAGES = [
    {"TITLE": "Contact", "URL": "contact"},
    {"TITLE": "Services", "URL": "services"},
    {"TITLE": "Projects", "URL": "projects"},
    {"TITLE": "About", "URL": "about"},
    {"TITLE": "External", "URL": "https://fsf.org"},
    {"TITLE": "My cool new link", "URL": "https://www.gnu.org/software/hurd"},
]
```
#### Internal links 

Internal links navigate to a page within the blog. We use the URL pattern names to identify which hyperlink should appear on the navigation.

To find a URL pattern name, look at your [URLconfs](https://docs.djangoproject.com/en/dev/topics/http/urls/#naming-url-patterns) within your Django app. 

Then, pass value to the URL field in settings, like so: 

URLconfs, return URL named index. 
```
re_path(r'^index/$', views.index, name='index')
```

Add index called inside main navigation. For example:
```
MAIN_NAVIGATION_PAGES = [
    {"TITLE": "Go Home", "URL": "index"},
...
```

#### External links

External links can allow navigation to any webpage. Supports HTTP, HTTPS, or FTP. 

Just remember to include the HTTP protocol at the beginning of an external link.

Add IBM.com to main navigation. For example:
```
MAIN_NAVIGATION_PAGES = [
    {"TITLE": "IBM", "URL": "https://ibm.com"},
...
```

#### Order of links

The pages on the navigation menu appear in the order of - first position in the settings list equals closest page on left on-screen.

In other words, from `config/settings`, the last element inside `MAIN_NAVIGATION_PAGES` will appear last in the menu and vice versa. 

To change the order, move the list elements accordingly. 

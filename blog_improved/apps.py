from django.apps import AppConfig
from django.conf import settings
class BlogConfig(AppConfig):
    name = "blog_improved"

    def ready(self):
        from blog_improved.conf.registry import insert_dependencies
        print(settings.INSTALLED_APPS)

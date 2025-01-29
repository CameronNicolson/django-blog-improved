from importlib import import_module 
from django.apps import AppConfig

class BlogConfig(AppConfig):
    name = "blog_improved"

    def ready(self):
        modules = ["blog_improved.api"]
        for module in modules:
            imported = import_module(module)

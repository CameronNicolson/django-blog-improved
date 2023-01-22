from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    #from blog.management.commands import build_groups
     #   cmd = build_groups.Command()
    from django.core.management import call_command
    call_command("build_groups")

class BlogConfig(AppConfig):
    name = "blog"

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)

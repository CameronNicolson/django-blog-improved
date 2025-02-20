from django.core.management import BaseCommand
from blog_improved.posts.models import Post
from blog_improved.authors.models import UserProfile
from blog_improved.models import BlogGroup
from blog_improved.conf import AUTHOR_DEFAULT_GROUP
from django.contrib.auth.models import Permission

GROUPS_PERMISSIONS = {
    AUTHOR_DEFAULT_GROUP: {
        Post: ['add', 'change', 'delete', 'view'],
        UserProfile: ['change', 'view'],
    },
}

class Command(BaseCommand):
    help = "Create default groups"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "-f",
            "--force",
            action='store_true',
            help="Force group to restore it's original settings",
        )

    def handle(self, *args, **options):

        self.stdout.write(self.style.MIGRATE_HEADING("Creating default blog groups and permissions"))
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:
            force = options["force"] or False
            # Get or create group
            group, created = BlogGroup.objects.get_or_create(name=group_name, status=1)

            if not created and not force:
                self.stdout.write("  No changes to apply.")
                return

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write("  Adding "
                                          + codename
                                          + " to group "
                                          + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")

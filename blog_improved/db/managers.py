from model_utils.managers import InheritanceManager
from blog_improved.models import Status

class PublicStatusManager(InheritanceManager):

    def include_status(self, status):
        status_list = [Status.PUBLISH]
        status_list.append(status)
        return self.get_queryset(status_list)
        
    def include_unlisted(self):
        return self.include_status(Status.UNLISTED)

    def get_queryset(self, status=[Status.PUBLISH]):
        return super().get_queryset().filter(status__in=status)



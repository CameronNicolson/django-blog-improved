from blog_improved.api.posts import PostViewSet
from blog_improved.api.settings import api_user_config_activated 
from rest_framework import routers

activated = api_user_config_activated()

def start(activated=activated):
    if not activated:
        return

    router = routers.DefaultRouter()
    router.register(r"posts", PostViewSet)

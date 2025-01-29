from django.urls import path, include
from blog_improved.models import Post
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ["author", "title", "content", "is_featured"]

# Default posts endpoint - return all public posts 
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.public.all()
    serializer_class = PostSerializer


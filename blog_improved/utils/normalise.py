from blog_improved.authors.models import PostAuthor
from blog_improved.posts.posts import Post
from blog_improved.posts.models import Post as PostModel

def normalise_post_entry(post):
    """Ensures `post` is always a Post, validating model consistency."""

    if isinstance(post, Post):
        return post

    # Convert from Django Post model to a blog_improved Post
    if isinstance(post, PostModel):
        return Post(
            slug=post.slug,
            title=post.title,
            content=post.content,
            created_on=post.created_on,
            updated_on=post.updated_on,
            published_on=post.published_on,
            headline=post.headline,
            category=post.category,
            is_featured=post.is_featured,
            author=post.author,
            cover_art=post.cover_art,
            tags=post.tags,
            status=post.status
        )

    # Convert dict to Post
    if isinstance(post, dict):
        if not post:
            return None

        return Post(
            slug=post.get("slug", None),
            title=post.get("title", ""),
            content=post.get("content", ""),
            author=post.get("author", PostAuthor()),
            created_on=post.get("created_on", ""),
            updated_on=post.get("updated_on", ""),
            published_on=post.get("published_on", ""),
            category=post.get("category", None),
            tags=post.get("tags", []),
            is_featured=post.get("is_featured", ""),
            headline=post.get("headline", ""),
            cover_art=post.get("cover_art", None),
            status=post.get("status", 0)
        )

    return None

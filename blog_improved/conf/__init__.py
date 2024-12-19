from blog_improved.conf.registry import register_app, insert_dependencies

register_app(
    name="blog_improved",
    description="A blogging platform",
    app_type=2,
    depends=["taggit"]
)

register_app(
    name="taggit",
    description="A tagging framework",
    app_type=1,
    depends=None
)

insert_dependencies("blog_improved")


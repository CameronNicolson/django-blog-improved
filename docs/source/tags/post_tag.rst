=========
Post Tag
=========

.. code-block:: django

   {% post id=911 %}


Retreive a single post as html.

When to use this tag?
---------------------
Use the post tag when you need to show a single post.

When not to use this tag?
-------------------------
When needing a list of posts, numerous post tags on a single page may be better accommodated by the :doc:`postlist_tag`.

Options for the ``{% post %}`` tag
-----------------------------------

- .. _post-tag-id-option:
  `id` (default: ""): Specifies the id of a given post used by its associated Post model. The id in most traditional django environments is the database index key.

Finding posts via ``{% post %}`` tag's context
-----------------------------------------------

Each post is typically resolved using a unique identifier derived from its title, a process known as slugification (or slugging) in app development.

Blog Improved leverages slugs to serve as a human-readable alternative to post IDs, making posts easier to recognise and use when writing database queries. For example:

.. code-block:: 

   Post: 
     id     =      57e311b7-68ca-44b7-b30e-9959e344c9e1, 
     title  =      Happy Birthday Claude, 
     slug   =      happy-birthday-claude



Notice in the example above that Claude's birthday post is easier to remember by its slug value rather than its ID.

How to use a slug
------------------

If the post tag's :ref:`option id <post-tag-id-option>` is not provided, a **slug value** must be passed to the renderer via context data to locate the corresponding post.

Passing context data in a Django view:

.. code-block:: python

    # <your-app-name>/views.py

    from blog_improved.constants import BLOG_POST_CONTEXT_NAME
    from django.shortcuts import render

    def my_view(request):
        context = {
            BLOG_POST_CONTEXT_NAME: {"slug": "happy-birthday-claude"}
        }
        return render(request, "single_post.html", context)


Using the context in a Django template:

.. code-block:: django

    <!-- templates/single_post.html -->

    {% post %}

If both a post's ID and slug are passed to the context data, the ID value takes precedence over the slug.

Supplying ``{% post %}`` Tag with Prefetched Data
--------------------------------------------------
Prefetching is the process of providing post data before the template rendering step takes place, bypassing the need for a lookup during template execution.

To supply a prefetched post, include a structured post object in Django’s context. By default, the entry is typically named "blog_improved_post". However, to avoid potential name conflicts, we recommend using the constant setting BLOG_POST_CONTEXT_NAME.

Example: Prefetching for an Event Website
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Consider an eating competition that sponsors its events online. Their website features an upcoming event using a view that renders a post through the {% post %} template tag.

Here’s how they can prefetch and supply the relevant post data:

.. code-block:: python

   # <your-app-name>/views.py

   from blog_improved.constants import BLOG_POST_CONTEXT_NAME 
   from blog_improved.posts.models import Post 
   from django.shortcuts import render

   def events_view(request): 
      next_event = Post.objects.filter(title__icontains="hot dog").order_by("-published_on").first() 
      context = {BLOG_POST_CONTEXT_NAME: next_event} 
      return render(request, "single_post.html", context)


Then in you template code:

.. code-block:: django

  <!-- templates/single_post.html -->

  {% post %}


In this example, prefetching allowed the event organisers to use a custom queryset sorted by recent dates. The {% post %} tag then processed the prefetched data, ensuring efficient rendering with the desired post content.

Example: Prefetching for dynamic posts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The {% post %} tag can also render a dynamically created `Post` object without retrieving it from the database. This can be useful for displaying temporary announcements, system messages, or content generated on the fly.

Consider a scenario where a website needs to display a scheduled maintenance message:

.. code-block:: python

   # <your-app-name>/views.py

   from datetime import datetime
   from blog_improved.posts.posts import Post
   from blog_improved.constants import BLOG_POST_CONTEXT_NAME
   from django.shortcuts import render

   def maintenance_view(request):
        Post(
                title="Maintenance Underway",
                headline="Maintenance is scheduled to end 7AM PST",
                content="We apologise for any inconvenience.",
                published_on=datetime(2025,11,12),
                created_on=datetime(2025,11,12),
                updated_on=datetime(2025,11,12),
                slug=None,
                category=None,
                is_featured=False,
                author=None,
                cover_art=None,
                tags=[],
                status=1
       )

       context = {BLOG_POST_CONTEXT_NAME: maintenance_post}
       return render(request, "maintenance_post.html", context)


.. code-block:: django

   # templates/maintenance_post.html
   {% post %}


Displaying Author Names in Posts
---------------------------------

When retrieving a post, an author's name can be displayed in two ways:

1. **Username** – The user's ``username`` field is shown.
2. **Full Name** – The user's ``first_name`` and ``last_name`` fields are shown together.

This system is designed to support privacy toggles for individual authors.

How Full Name Display Works
---------------------------

The display mode is determined by the author's **public profile settings**.
For a post to display the author's full name, all of the following conditions must be met:

- The author **has a user profile** associated with their account.
- The **public status** is enabled in their user profile settings.
- The **``first_name`` and ``last_name`` fields** in the User model are both correctly filled.

If any of these conditions are not met, the author's posts will **default to displaying their username** instead of their full name.

Using "as" for Saving a Post Model in Context Data
---------------------------------------------------
Using the as keyword with a post-related tag allows you to efficiently save a Post model instance to the template context. This makes it easier to reference the post multiple times within the same template without executing additional lookups.

.. code-block:: django

   <!-- example-template.html -->
   {% post as latest_post %}

   <article>
      <header>
        <h2>{{ latest_post.title }}</h2>
      </header>
      <section>
          <p>{{ latest_post.content }}</p>
      </section>
      <footer>
          <p>Author: {{ latest_post.author }}</p>
          <p>Published on: {{ latest_post.created_at }}</p>
      </footer>
   </article>


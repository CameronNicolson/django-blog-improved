=================
Postlist tag
=================

.. code-block:: html

   {% postlist %}

Retrieves html of the latest posts, or posts matching the given criteria.

Options for the ``{% postlist %}`` Template Tag
------------------------------------------------

- `category` (default: ""): Specifies the category of posts to display. For example, ``category="car"`` filters the posts to only those in the "car" category.
- `ignore_category` (default: ""): Specifies the category to exclude from the retrieved posts. For example, ``ignore_category="retro"`` ensures posts in the "retro" category are omitted.
- `max_count` (default: -1): Defines the maximum number of posts to retrieve. For example, ``max_count="3"`` limits the output to three posts.
- `sort` (default: "model"): Determines the sorting order of the posts. Common values include ``"asc"`` (alphabetical order by title) and ``"desc"`` (reverse alphabetical order).

- `featured` (default: False): If set to ``True``, retrieves a featured post relevant to the retrieved posts.

- `featured_count` (default: ``1``): Determines the number of featured posts to return when ``featured=True``. For example, ``featured_count=7`` retrieves up to seven featured posts.

- `name` (default: ""): Defines a group identifier for the posts. Useful for targeting specific lists during parsing.

- `layout` (default: "default"): Specifies the presentation layout that the renderer will follow. For example, ``layout="standard_3by3"`` arranges the posts in exactly three rows and three columns.

- `layout_format` (default: "grid"): Determines the structural format of the displayed posts. If set to ``"list"``, posts are wrapped in list and list-item elements. If set to ``"grid"``, posts are placed in a grid layout.

The Kitchen Sink
----------------

If you want to see all options in action, here’s an example using everything at once:

.. code-block:: django

    {% postlist category="tech" max_count=5 featured=True featured_count=2 sort="desc" name="technews" layout="standard_4by4" layout_format="grid" %}

This example retrieves up to 5 posts in the "tech" category, the first 2 are of type featured, orders them by title in descending order, uses a fours rows by four columns layout, and assigns the group id as "technews".

When to use this tag?
---------------------
Use the postlist tag when you need to show a posts organised in a grid format.

Format as a flat list
----------------------
Make the list a one-dimensional linear structure. This will wrap the posts in an unordered list `ul`.

.. code-block:: html

   {% postlist tag layout_format='list' %}

Register a custom layout
------------------------

Additional layouts can be registered and reused with the post list. 

.. code-block:: python

   from blog_improved.presentation import GridLayout, layout_presets
   from blog_improved.presentation import Spacing, Border
   from blog_improved.posts.post_list_markup_presets import layout_presets
   
   custom_layout = GridLayout(
                        padding=Spacing(15,10,15,10)
                        margin=Spacing(10,10,10,10)
                        border=Border(33, "dashed")
                        row=50,
                        columns=20
                        )

   layout_presets["custom_layout"] = custom_layout 

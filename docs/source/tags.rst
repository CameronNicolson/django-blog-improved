=====
Tags
=====

Templates often contain placeholders that the server dynamically replaces with computed values. These placeholders are known as template tags, which allow embedding logic, data, or structure within the template while keeping the logic separate from the presentation layer. A common example is displaying dates; for instance, you might see {% date_now %} evaluating to the current date and time.

Blog Improved builds on this concept by providing a powerful set of template tags designed specifically for managing and displaying blog posts. These tags enable any page on your website to seamlessly integrate dynamic blog content. The following sections outline the available tags and their options.

.. toctree::
   :maxdepth: 2
   :caption: Tags

   tags/post_tag
   tags/postlist_tag

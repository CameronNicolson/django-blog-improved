from django.template.base import Node
from blog_improved.helpers.html_generator import SgmlGenerator

def hyperlink_wrapper(sgml:SgmlGenerator, hyperlink:str, prepend_to:Node) -> Node:
    if prepend_to is None:
        return None
    if hyperlink:
        link_node = sgml.create_node(
            "hyperlink",
            attributes={
                "class": "link",
                "href": hyperlink,
            })            
        link_node.add_child(prepend_to)
        return link_node
    else:
        return prepend_to


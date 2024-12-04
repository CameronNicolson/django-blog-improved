import django.template.base import Node
import blog_improved.helpers.html_generator import SgmlGenerator

def hyperlink_wrapper(self, sgml:SgmlGenerator, hyperlink:str, description:str, prepend_to:Node) -> Node:
    if hyperlink:
        link_node = sgml.create_node(
            "hyperlink",
            attributes={
                "title": description, 
                "href": hyperlink,
            })            
        link_node.add_child(prepend_to)
        return link_node
    else:
        return prepend_to


from blog_improved.formatters.html.html_generator import SgmlGenerator
from blog_improved.formatters.markup import MarkupNode

def bool_wrapper(
    sgml: SgmlGenerator,
    condition: bool,
    wrapper_node_name: str,
    attributes: dict,
    append_to: MarkupNode
) -> MarkupNode:
    """
    Wraps a given Node with another Node based on a boolean condition.

    :param sgml: An instance of SgmlGenerator to create new nodes.
    :param condition: A boolean value to decide whether to wrap the node.
    :param wrapper_node_name: The name of the wrapping node (e.g., "hyperlink").
    :param attributes: A dictionary of attributes for the wrapping node.
    :param append_to: The Node to be wrapped.
    :return: The wrapped Node or the original Node if condition is False.
    """
    if append_to is None:
        return None
    if condition:
        wrapper_node = sgml.create_node(
            wrapper_node_name,
            attributes=attributes,
        )
        wrapper_node.add_child(append_to)
        return wrapper_node
    return append_to


from .presentation_strategy import PresentationStrategy, Rect

class InlinePresentation(PresentationStrategy):
    """
    A strategy that applies basic inline styles directly.
    """

    def move_position(self, sgml_element, pos: Rect):
        width = pos.width
        if width:
            current_style = sgml_element.attrs.get("style", "")
            sgml_element.attrs["style"] = f"{current_style} width: {pos.width}%;"


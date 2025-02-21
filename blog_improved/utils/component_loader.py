from blog_improved.formatters.html.html_generator import HtmlGenerator, make_standard_element
from blog_improved.presentation.inline_presentation import InlinePresentation
from blog_improved.presentation.css_presentation import CssPresentation, CssElementModifier

GENERATOR_MAPPING = {
    "html": HtmlGenerator,
}

PRESENTATION_STRATEGY_MAPPING = {
    "inline": InlinePresentation,
    "css": CssElementModifier
}

def get_presentation_strategy(strategy_type):
    strategy_type = strategy_type.lower()
    return PRESENTATION_STRATEGY_MAPPING[strategy_type]()

def get_sgml_generator(generator_type, element_composer=make_standard_element):
    generator_type = generator_type.lower()
    return GENERATOR_MAPPING[generator_type](element_composer=element_composer)

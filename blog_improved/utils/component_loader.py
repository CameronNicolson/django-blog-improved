from blog_improved.helpers.html_generator import HtmlGenerator, make_standard_element

GENERATOR_MAPPING = {
    "html": HtmlGenerator,
}

def get_sgml_generator(generator_type):
    generator_type = generator_type.lower()
    return GENERATOR_MAPPING[generator_type](element_composer=make_standard_element)

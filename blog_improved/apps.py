from django.apps import AppConfig
from pathlib import Path
from blog_improved.themes.settings import load_theme, get_theme
from blog_improved.conf import get_theme_settings
from blog_improved.utils.component_loader import get_sgml_generator, get_presentation_strategy
from blog_improved.utils.theme_intergration  import get_theme_width_map, get_theme_grid, integrate_theme_with_generator
from django.conf import settings
from blog_improved import conf
from blog_improved.formatters.env import Env
from blog_improved.utils.math import RangeClamper
from blog_improved.presentation.css_presentation import CssElementModifier, GridClassName

class BlogConfig(AppConfig):
    name = "blog_improved"
    

    def ready(self):
        load_theme("fixme")
        #integrate_theme_with_generator(get_theme(), formatter.format)

from django.apps import AppConfig
from pathlib import Path
from blog_improved.themes.settings import load_theme, get_theme
from blog_improved.conf import get_theme_settings
from blog_improved.utils.component_loader import get_sgml_generator
from blog_improved.utils.theme_intergration  import get_theme_width_map, get_theme_grid, integrate_theme_with_generator
import blog_improved.helpers.html_generator as html_gen

class BlogConfig(AppConfig):
    name = "blog_improved"
    sgml_generator = None

    def ready(self):
        load_theme("fixme")
        self.sgml_generator = get_sgml_generator("html")  
        integrate_theme_with_generator(get_theme(), self.sgml_generator)
        # MONKEY PATCHING - STOOPID WHAT THE HELL
        html_gen.get_width_map = get_theme_width_map 
        html_gen.get_grid_config = get_theme_grid

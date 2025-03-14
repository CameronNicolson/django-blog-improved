from django.apps import AppConfig
from pathlib import Path
from blog_improved.conf import get_theme_settings
from blog_improved.utils.component_loader import get_sgml_generator, get_presentation_strategy
from django.conf import settings
from blog_improved import conf
from blog_improved.formatters.env import Env
from blog_improved.utils.math import RangeClamper
from blog_improved.presentation.css_presentation import CssElementModifier, GridClassName

class BlogConfig(AppConfig):
    name = "blog_improved"
 
    def ready(self):
        from blog_improved.file_manager import get_data_file_manager, setup_file_manager
        setup_file_manager()

from .html.html_generator import BlogHtmlFactory
from .html.html_generator import HtmlGenerator, make_standard_element 
from blog_improved.presentation.inline_presentation import InlinePresentation 
from .settings import _formatter_env_settings, get_env_setting

_env = None

class Env:
    def __init__(self, config):
        if not isinstance(config, dict):
            raise ValueError("Env must be initialized with a config dictionary.")

        self.config = config
        self._markup = None
        self._blog_factory = None
    
    @property
    def blog_factory(self):
        if self._blog_factory is None:
            self._blog_factory = self._init_blog_html_factory()
        return self._blog_factory

    @property
    def markup(self):
        if self._markup is None:
            self._markup = self._init_markup()
        return self._markup 
    
    def _init_markup(self):
        element_composer = self.config.get("element_composer")
        sgml_generator = self.config.get("sgml_generator")
        return sgml_generator(element_composer=element_composer) 

    def _init_blog_html_factory(self):
        """Private method to create a BlogHtmlFactory instance. Should not be called directly."""
        sgml_generator = self.markup
        strategy = self.config.get("presentation_strategy")
        strategy = strategy()
        return BlogHtmlFactory(sgml_generator, presentation_strategy=strategy)



    def get_setting(self, setting_name):
        return self.config.get(setting_name)


def get_env():
    global _env
    if _env is None:
        config = {}

        env_settings_keys = list(_formatter_env_settings.keys())
        for setting_name in env_settings_keys:
            value = get_env_setting(setting_name)
            if value is not None:
                config[setting_name] = value

        defaults = {
            "element_composer": make_standard_element, 
            "sgml_generator": HtmlGenerator,
            "presentation_strategy": InlinePresentation,
        }

        for setting_name, default_value in defaults.items():
            if setting_name not in config or config[setting_name] is None: 
                config[setting_name] = default_value

        _env = Env(config)
    return _env


from dataclasses import dataclass
from typing import Dict, List
from django.conf import settings as django_settings
from importlib import import_module
from collections import defaultdict, deque

registry: Dict[str, "SettingsApp"] = {}

@dataclass
class SettingsApp:
    name:str
    description:str
    app_type:int
    depends:List[str]

    def __lt__(self, other):
        return self.app_type < other.app_type


def register_app(
    name=None,
    description=None,
    app_type=None,
    depends=None,
):
    """
    Registers an app with its dependencies.
    """
    if name is None:
        raise TypeError(
            "blog_improved.conf.register_setting requires the " "'name' keyword argument."
        )
    if app_type is None:
        raise TypeError(
            "blog_improved.conf.register_setting requires the " "'name' keyword argument."
        )
    elif not isinstance(app_type, int):
        # An int or long or subclass on Py2
        raise TypeError(
            "blog_improved.conf.register_setting requires the " "'name' keyword argument."
        )
    
    registry[name] = SettingsApp(
        name,
        description or "",
        app_type,
        depends or [] 
    )


def resolve_dependencies(app_name: str, resolved=None, unresolved=None) -> List[str]:
    """
    Recursively resolves dependencies for the given app.
    """
    if resolved is None:
        resolved = []
    if unresolved is None:
        unresolved = []

    app = registry.get(app_name)
    if not app:
        raise ValueError(f"App '{app_name}' is not registered.")

    unresolved.append(app_name)
    for dep in app.depends:
        if dep not in resolved:
            if dep in unresolved:
                raise ValueError(f"Circular dependency detected: {dep} -> {app_name}")
            resolve_dependencies(dep, resolved, unresolved)
    resolved.append(app_name)
    unresolved.remove(app_name)

    return resolved


def insert_dependencies(app_name: str):
    """
    Inserts dependencies for the given app before it in INSTALLED_APPS.
    """
    if app_name not in registry:
        raise ValueError(f"App '{app_name}' is not registered.")

    # Resolve dependencies
    dependencies = resolve_dependencies(app_name)

    # Insert dependencies into INSTALLED_APPS
    installed_apps = list(django_settings.INSTALLED_APPS)
    if app_name not in installed_apps:
        raise ValueError(f"App '{app_name}' must be in INSTALLED_APPS.")

    app_index = installed_apps.index(app_name)
    for dep in dependencies:
        if dep != app_name and dep not in installed_apps:
            installed_apps.insert(app_index, dep)
            app_index += 1  # Adjust index for subsequent inserts

    django_settings.INSTALLED_APPS = installed_apps


#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent 
EXAMPLES_DIR = BASE_DIR / "examples"

def find_and_parse_entrypoints(path: Path):
    """
    Recursively look for files named 'entrypoint.example' in the given path,
    parse their JSON contents into a single dict, and append to a list.

    Args:
        path (Path): The starting path to search (can be a directory).

    Returns:
        list: A list of dictionaries parsed from 'entrypoint.example' files.
    """
    entries = []

    # Recursively search for 'entrypoint.example' files
    for file in path.rglob("entrypoint.example"):
        if file.is_file():
            try:
                # Parse the JSON content of the file
                with file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):  # Ensure it's a dictionary
                        entries.append(data)
                    else:
                        print(f"Skipped {file}: JSON is not a dictionary.")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in {file}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file}: {e}")

    return entries

# Get all fixture paths from FIXTURE_DIRS
def get_all_fixtures(settings):
    fixture_files = []
    sorted_fixtures = []
    fixture_order = ["users.yaml", "groups.yaml", "redirects.yaml", "media.yaml", "tags.yaml", "posts.yaml"]
    preferred = lambda fixture: fixture_order.index(fixture.split("/")[-1]) if fixture.split("/")[-1] in fixture_order else len(fixture_order) 
    for fixture_dir in settings.FIXTURE_DIRS:
        for root, dirs, files in os.walk(fixture_dir):
            fixture_files = [f"{root}/{f}" for f in files]
    for i, file in enumerate(fixture_files):
        if not file.endswith(".yaml"):
            fixture_files.remove(i)
    for file in sorted(fixture_files, key=preferred):
        sorted_fixtures.append(file)
    return sorted_fixtures

def set_templates(templates, examples):
    # The new directory to add
    default_template_dir = EXAMPLES_DIR / "templates"
    new_template_dirs = [default_template_dir]
    # Get the templates from examples
    for example in examples:
        template_dir = example["path"]
        if template_dir and (EXAMPLES_DIR / template_dir).exists():
            new_template_dirs.append(EXAMPLES_DIR / template_dir)
    # Get the existing template directories from the settings
    template_dirs = []
    for template_config in templates:
        dirs = template_config.get("DIRS", [])
        template_dirs.extend(dirs)

    # Check if the directory already exists in TEMPLATES
    for template in new_template_dirs:
        if template not in template_dirs:
            for template_config in templates:
                if "DIRS" in template_config:
                    template_config["DIRS"].append(template)
                    break


def main():
    """Run administrative tasks."""
    sys.path.append(os.path.dirname("examples")) 
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    settings.EXAMPLES = find_and_parse_entrypoints(EXAMPLES_DIR)
    set_templates(settings.TEMPLATES, settings.EXAMPLES)
    urls = "examples.urls"
    settings.ROOT_URLCONF = urls
    settings.STATIC_ROOT = EXAMPLES_DIR / "staticfiles"
    settings.STATICFILES_DIRS = [
        EXAMPLES_DIR / "static/",
    ]
    settings.INSTALLED_APPS.append("django.contrib.staticfiles")
    command = ["django", "testserver"]
    for fixture in get_all_fixtures(settings):
        command.append(fixture)
    execute_from_command_line(command)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""Django's examples runner."""
import os
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent 
EXAMPLES_DIR = BASE_DIR / "examples"

def find_and_parse_entrypoints(path: Path, settings: dict):
    """
    Recursively look for files named 'entrypoint.example' in the given path,
    parse their JSON contents into a single dict, and append to a list.

    Args:
        path (Path): The starting path to search (can be a directory).

    Returns:
        list: A list of dictionaries parsed from 'entrypoint.example' files.
    """
    entries = dict()
    groups = dict()

    # Recursively search for 'entrypoint.example' files
    for file in path.rglob("entrypoint.example"):
        if file.is_file():
            try:
                # Parse the JSON content of the file
                with file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):  # Ensure it's a dictionary
                        path = data["path"].split("/")[:2]
                        group = path[0]
                        name = path[1]
                        ident = str(group + name).lower()
                        entries[ident] = data
                        try:
                            group_name = data["group"]
                            groups[group_name].append(data)
                        except KeyError:
                            groups[data["group"]] = list([data])
                        for fixture_dir in settings.FIXTURE_DIRS:
                            parts = str(fixture_dir).split("/")[-3:]
                            # discard last part which is "fixture"
                            if ident in "".join([parts[0], parts[1]]):
                                entries[ident]["fixtures"] = {"fixture_path": fixture_dir}
                                if os.path.isdir(fixture_dir):
                        # Iterate through all .json files in the directory
                                    for filename in os.listdir(fixture_dir):
                                        if filename.endswith(".json"):
                                            try: 
                                                entries[ident]["fixtures"]["files"].append(filename)
                                            except KeyError:
                                                entries[ident]["fixtures"]["files"] = [filename]
                        else:
                            print(f"Skipped: no fixtures in {ident} example directory.")

                    else:
                        print(f"Skipped {file}: JSON is not a dictionary.")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in {file}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file}: {e}")
    return (groups, entries)

def find_example_fixtures_dirs(root_dir, settings):
    fixture_dirs = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "fixtures" in dirnames:
            fixture_dirs.append(Path(os.path.abspath(os.path.join(dirpath, "fixtures"))))
    for f in fixture_dirs:
        settings.FIXTURE_DIRS.append(f)

    return fixture_dirs

# Get all fixture paths from FIXTURE_DIRS
def get_all_fixtures(settings):
    fixture_files = []
    sorted_fixtures = []
    ignore_dirs = ["html"]
    fixture_order = ["users.yaml", "groups.yaml", "redirects.yaml", "media.yaml", "tags.yaml", "posts.yaml"]

    # Function to determine the sort order
    preferred = lambda fixture: fixture_order.index(fixture.split("/")[-1]) if fixture.split("/")[-1] in fixture_order else len(fixture_order)
    for fixture_dir in settings.FIXTURE_DIRS:
        # List all files and directories in the root folder
        for entry in os.listdir(fixture_dir):
            entry_path = os.path.join(fixture_dir, entry)

            # Skip directories (e.g., "html")
            if os.path.isdir(entry_path) and entry in ignore_dirs:
                continue

            # Add files with .yaml extension
            if os.path.isfile(entry_path) and entry.endswith(".yaml"):
                fixture_files.append(entry_path)

    # Sort the files based on the preferred order
    sorted_fixtures = sorted(fixture_files, key=preferred)

    return sorted_fixtures

def set_templates(templates, examples):
    # The new directory to add
    default_template_dir = EXAMPLES_DIR / "templates"
    new_template_dirs = [default_template_dir]
    # Get the templates from examples
    for example in examples.values():
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

def create_sample_databases(settings):
    """
    Dynamically adds a new database, runs migrations, and loads fixtures.

    Args:
        ident (str): The identifier for the database entry.
        entries (dict): The dictionary containing fixture details.
    """
    from django.core.management import execute_from_command_line, call_command

    entries = settings.EXAMPLES or []
    for key, entry in entries.items():
        fixture_path = None
        fixture_files = None 
        if "fixtures" in entry and "fixture_path" in entry["fixtures"]:
            fixture_path = entry["fixtures"]["fixture_path"]
            fixture_files = entry["fixtures"]["files"]
        if fixture_path == None:
            continue
        # Ensure the directory exists
        if not os.path.isdir(fixture_path):
            print(f"Warning: Fixture path '{fixture_path}' does not exist.")
            return

        # Generate the new database name
        ident = key
        db_name = f"{key}_db"

        # Add new database dynamically
        settings.DATABASES[db_name] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "examples" / "data" / f"{key}.sqlite3",
            "TEST": {
            "NAME": BASE_DIR / "examples" / "data" / f"{key}.sqlite3",
            "MIGRATE": True
            }
        }
        entry["database"] = db_name

        print(f"Added database '{db_name}' at {settings.DATABASES[db_name]['NAME']}")

        # Set the default database to the new database
        settings.DATABASES["default"]["NAME"] = settings.DATABASES[db_name]["NAME"]
        settings.DATABASES["default"]["TEST"] = {
        "NAME": settings.DATABASES[db_name]["NAME"],
        "MIGRATE": True,
        }
    
        # Run migrations for the new database
        execute_from_command_line(["django", "migrate", "--run-syncdb"])
  
        full_fixture_paths = [os.path.join(fixture_path, filename) for filename in fixture_files]

        if fixture_files:
            call_command("loaddata", *full_fixture_paths)
        else:
            print(f"No JSON fixtures found in.")

def set_debug_toolbar(settings):
    try:
        from debug_toolbar import toolbar
    except Exception as e:
        print(e)
        traceback.print_exc()
        return
    settings.DATABASE_ROUTERS = ["examples.middleware.database_middleware.DatabaseSwitcher"]
    settings.INSTALLED_APPS.append("debug_toolbar")
    settings.MIDDLEWARE.append("examples.middleware.database_middleware.DynamicDatabaseMiddleware")
    settings.MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    settings.MIDDLEWARE.append("examples.middleware.debug_reverse_override.DebugReverseOverrideMiddleware")

    settings.RENDER_PANELS = True

    settings.DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
    }

    # Find the first template backend (DjangoTemplates)
    for template_engine in settings.TEMPLATES:
        if template_engine['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
            # Add the debug context processor dynamically
            template_engine['OPTIONS']['context_processors'].append(
            'django.template.context_processors.debug'
        )

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
    example_fixtures = find_example_fixtures_dirs("examples", settings)
    settings.EXAMPLE_GROUPS, settings.EXAMPLES = find_and_parse_entrypoints(EXAMPLES_DIR, settings)
    set_templates(settings.TEMPLATES, settings.EXAMPLES)
    urls = "examples.urls"
    settings.ROOT_URLCONF = urls
    settings.STATIC_ROOT = EXAMPLES_DIR / "staticfiles"
    settings.STATICFILES_DIRS = [
        EXAMPLES_DIR / "static/",
    ]
    settings.INSTALLED_APPS.append("django.contrib.staticfiles")
    settings.INSTALLED_APPS.append("examples.core")
    set_debug_toolbar(settings)

    settings.DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "examples" / "data" / "default.sqlite3",
    },
    "normal": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "examples" / "data" / "default.sqlite3",
    },
    }
    settings.DATABASES["default"]["NAME"] = settings.DATABASES["normal"]["NAME"]
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line 
        create_sample_databases(settings)
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        return

    settings.DATABASES["default"]["NAME"] = settings.DATABASES["normal"]["NAME"]
    settings.DATABASES["default"]["TEST"] = {
    "NAME": settings.DATABASES["normal"]["NAME"],  # Force it to use db1.sqlite3
    "MIGRATE": True,
    }


    command = ["django", "testserver"]
    for fixture in get_all_fixtures(settings):
        command.append(fixture)
    execute_from_command_line(command)

if __name__ == '__main__':
    main()

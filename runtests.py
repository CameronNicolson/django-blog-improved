#!/usr/bin/env python
import os
import sys
import importlib.util
from typing import Optional, Tuple
import django
from django.conf import settings
from django.test.utils import get_runner


def check_package_path(package_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if a Python package is installed and get its path.

    Args:
        package_name (str): Name of the package to check

    Returns:
        Tuple containing:
        - bool: True if package is found, False otherwise
        - Optional[str]: Package path if found, None otherwise
        - Optional[str]: Error message if there was an issue, None otherwise
    """
    try:
        # Try to find the package specification
        spec = importlib.util.find_spec(package_name)

        if spec is None:
            return False, None, f"Package '{package_name}' not found in Python path"

        # Get the package location
        if spec.origin is None:
            return False, None, f"Package '{package_name}' found but has no origin location"

        # Return success with package path
        return True, spec.origin, None

    except ImportError as e:
        return False, None, f"Import error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"

def verify_package(package_name: str) -> None:
    """
    Verify a package exists and raise an error if it doesn't.

    Args:
        package_name (str): Name of the package to verify

    Raises:
        ImportError: If the package is not found or there's an error importing it
    """
    found, path, error = check_package_path(package_name)

    if not found:
        raise ImportError(error)

def check_dependencies():
    required_pkgs = [
            "yaml",
             "bs4"
    ]
    for pkg in required_pkgs:
        try:
            verify_package(pkg)
        except ImportError:
            print(f"{pkg} library was not found and is required"\
                " by the tests. \nDid you remember to install the"\
                + " dependencies? \nTry running "\
                + "pip install -r tests/requirements.txt")
            exit(0)

if __name__ == "__main__":
    sys.path.append(os.path.dirname("tests"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    check_dependencies()
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner() 
    failures = None
    if len(sys.argv) > 1:
        from tests.suite import suite
        argument = sys.argv[1]
        failures = test_runner.run_suite(suite(argument))
    else:
        failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))



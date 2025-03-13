from pathlib import Path

ROOT_DIR = Path.cwd() / "tests" 
FIXTURES_DIR = ROOT_DIR / "fixtures"

def load_fixture(filename):
    file = FIXTURES_DIR / filename
    with open(file, "r") as f:
        return f.read()

def get_fixture_path(filename):
    path = FIXTURES_DIR / filename
    assert path.exists()
    return path


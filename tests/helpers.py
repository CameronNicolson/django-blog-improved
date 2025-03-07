from pathlib import Path

def load_fixture(filename):
    file = Path.cwd() / "tests" / "fixtures" / filename
    with open(file, "r") as f:
        return f.read()

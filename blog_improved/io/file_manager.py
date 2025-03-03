import os
from pathlib import Path
from enum import Enum

class FileManager:
    def __init__(self):
        self._mappings = {}  # Virtual dir -> Real system path

    def add_virtual_directory(self, virtual_path: str, real_path: Path):
        """Maps a virtual directory (e.g., 'data/music/') to a real location on disk."""
        if not real_path.exists():
            raise ValueError(f"Real path {real_path} does not exist!")
        self._mappings[virtual_path] = real_path

    def resolve_virtual_path(self, virtual_path: str) -> Path:
        """Resolves a virtual directory to its actual system path."""
        if virtual_path in self._mappings:
            return self._mappings[virtual_path]
        raise ValueError(f"Virtual path '{virtual_path}' not found in mappings!")

    def find_file(self, filename: str, virtual_path: str) -> tuple:
        """Finds a file inside a virtual directory by resolving to real path."""
        if virtual_path not in self._mappings:
            return False, ""

        real_path = self._mappings[virtual_path]
        file_path = real_path / filename

        if file_path.exists():
            return True, str(file_path)
        return False, ""

    def list_virtual_dirs(self):
        """Lists all virtual directories and their real locations."""
        return self._mappings

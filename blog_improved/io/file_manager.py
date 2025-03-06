import re
import os
import io
from abc import ABC
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from blog_improved.utils.tree import Tree, DfsIterator

class FileValidator(ABC):
    def is_valid(self, path_to_file) -> bool:
        raise NotImplemented()

class NoFileValidation(FileValidator):
    def is_valid(self, path_to_file):
        return True

class FileHandler:
    def is_accepted_file(self, path_to_file, validator):
        raise NotImplemented()

    def open(self, path_to_file):
        raise NotImplemented()

class FileReader:
    def __init__(self):
        pass

class FileOpenOccupyBuffer(FileHandler): 
    def is_accepted_file(self, path_to_file, validator):
        return validator.is_valid(path_to_file)

    def open(self, path_to_file) -> FileReader: 
        file = open(path_to_file, "r", encoding="utf-8")
        return file

@dataclass
class VirtualFSNode:
    fs_type: str
    virtual_path: str
    system_path: Path
    
    def is_dir(self):
        return self.fs_type.lower() == "dir"

    def is_file(self):
        return self.fs_type.lower() == "file"

    def is_same_virtual_path(self, other):
        return self.virtual_path == other.virtual_path

class FileManager:
    """FileManager is a virtual interface for directories, mapped to real system paths"""
    def __init__(self):
        self._mappings = Tree(value=VirtualFSNode(fs_type="dir", virtual_path="/", system_path="")) 
        self._file_handler = FileOpenOccupyBuffer
   
    def _split_path(self, path:str):
        path.strip() # clear edge whitespace
        is_rooted = path.startswith("/")
        parts = path.strip("/").split("/") if path != "/" else []
        return ["/"] + parts if is_rooted else parts

    def _find_virtual_node(self, virtual_path: str):
        """Finds and returns the last existing node along the virtual path."""
        paths = self._split_path(virtual_path)
        cwd = self._mappings
        full_path = ""

        while paths:
            pathname = paths.pop(0)
            full_path = full_path.rstrip("/$") + "/" + pathname if pathname != "/" else "/"

            current_dir = VirtualFSNode(fs_type="dir", virtual_path=full_path, system_path="")
            node = self._mappings.search(current_dir.is_same_virtual_path)

            if node:
                cwd = node
            else:
                return None  # Stop if a directory in the path is missing

        return cwd

    def add_virtual_directory(self, virtual_path: str, real_path: Path):
        """Maps a virtual directory (e.g., 'data/music/') to a real location on the system's disk."""
        if not real_path.exists():
            raise ValueError(f"Real path {real_path} does not exist!")
        if not real_path.is_dir():
            raise ValueError(f"Real path {real_path} is not a directory!")

        parent_path = "/".join(self._split_path(virtual_path)[:-1]) or ""
        parent_node = self._find_virtual_node(parent_path)

        if parent_node is None:
            raise ValueError(f"Cannot create directory \"{virtual_path}\", parent directory \"{parent_path}\" does not exist.")

        new_dir = VirtualFSNode(fs_type="dir", virtual_path=virtual_path, system_path=real_path)
        parent_node.add_child(new_dir)

    def add_virtual_file(self, virtual_path: str, real_path: Path):
        """Maps a virtual file to a real system file."""
        if not real_path.exists():
            raise ValueError(f"Real path {real_path} does not exist!")
        if not real_path.is_file():
            raise ValueError(f"Real path {real_path} is not a file!")

        paths = self._split_path(virtual_path)
        filename = paths.pop()  # Extract the file name
        parent_path = "/".join(paths) or "/"

        parent_node = self._find_virtual_node(parent_path)

        if parent_node is None:
            raise ValueError(f"Cannot create file \"{virtual_path}\", parent directory \"{parent_path}\" does not exist.")

        new_file = VirtualFSNode(fs_type="file", virtual_path=virtual_path, system_path=real_path)
        parent_node.add_child(new_file)

    def resolve_virtual_path(self, virtual_path: str) -> Path:
        """Resolves a virtual directory to its actual system path."""
        virtual_path = re.sub("/$", "", virtual_path)
        for virtual_fs in DfsIterator(self._mappings):
            if virtual_fs is None:
                continue
            if virtual_fs.virtual_path == virtual_path:
                return virtual_fs.system_path 
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

from .standard_assets import StandardAssets
from pathlib import Path
import os

class DataDirectoryManager:
    """Handles detection and validation of the /data/ directory"""

    STANDARD_LOCATIONS = [
        Path("./data/"),
        Path("../data/"),
        Path("../../data/"),
        Path(__file__).resolve().parent / "data"
    ]
    
    @staticmethod
    def discover_paths(search_dirnames:list[str]) -> list[Path]:
        subdirs:list[Path] = list() 
        num_names:int = len(search_dirnames)
        dir_found:list[bool] = [False for _ in range(num_names)]
        root_dir = DataDirectoryManager.find_data_directory() 
        for index,item in enumerate(search_dirnames):
            if not dir_found[index] and (root_dir / item).exists():
                dir_found[index] = True
                subdirs.append(root_dir / item)
        return subdirs

    @staticmethod
    def find_data_directory() -> Path:
        """Finds the appropriate data directory"""
        env_path = os.environ.get("BLOG_DATADIR")
        if env_path:
            return Path(env_path) / "data"

        for path in DataDirectoryManager.STANDARD_LOCATIONS:
            if path.exists():
                return path

        print("Could not find the /data/ directory in standard locations.")
        print("Set environment variable $BLOG_DATADIR to point to the directory.")
        exit(1)  # Stop execution if no valid path is found

    @staticmethod
    def validate_data_directory(path: Path, subdirs: list[str]):
        """Ensures the path is a valid /data/ directory"""
        if not path.exists():
            raise ValueError(f"Invalid data directory: {path}")
        if path.name != "data":
            raise ValueError(f"Expected 'data' directory, but found {path.name}")

        for subdir in subdirs:
            if not (path / subdir).is_dir():
                raise ValueError(f"Not found: missing data subdirectory: {subdir}")


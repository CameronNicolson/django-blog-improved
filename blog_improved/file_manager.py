from blog_improved.io.file_manager import FileManager
from blog_improved.io.data_directory_manager import DataDirectoryManager
from django.conf import settings

def setup_file_manager():
    file_manager = FileManager()
    env_path = getattr(settings, "BLOG_DATA_DIR", None)

    if env_path:
        DataDirectoryManager.STANDARD_LOCATIONS.append(Path(env_path))

    data_directory = DataDirectoryManager.find_data_directory()

    if data_directory:
        file_manager.add_virtual_directory("/data", data_directory)
        discovered_asset_dirs = DataDirectoryManager.discover_paths(StandardAssets().get())

        for directory in discovered_asset_dirs:
            file_managerr.add_virtual_directory(directory.name, directory)

    global _file_manager_instance
    _file_manager_instance = file_manager

def get_data_file_manager():
    global _file_manager_instance
    return _file_manager_instance

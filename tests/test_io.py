import unittest
import tempfile
import os
import tomllib
from enum import Enum
from blog_improved.io.standard_assets import AssetType, StandardAssets
from blog_improved.io.file_manager import FileManager
from blog_improved.io.data_directory_manager import DataDirectoryManager
from django.test import TestCase
from pathlib import Path

classic_theme_file = """
name = "classic"
authors = ["Cameron Nicolson"]
license = "BSD-1-Clause"
version = "0.1.0"
variant = "" 

[media_licenses]
background.jpg = "CC-BY-NC-4.0"

[media_attributions]
background.jpg = "Jo Doe - CC-BY-4.0 - https://example.local/art"
"""

#def create_junk_file(path: Path, contents):
#    if contents == "":
#        text = math.random()


class TestStandardAssets(TestCase):

    def setUp(self):
        """Setup a new StandardAssets instance before each test"""
        self.asset = StandardAssets()
        # Add a temporary directory to the standard locations
        self.tmp_dir = Path(tempfile.gettempdir())  # Uses system's temporary directory



    def test_initialization(self):
        """Test if the StandardAssets initializes correctly"""
        self.assertEqual(len(self.asset._asset_dirs), AssetType.ASSET_COUNT.value)
        self.assertEqual(self.asset._asset_dirs[AssetType.THEMES.value], "themes")

    def test_get_asset_dir_name_with_enum(self):
        """Test retrieving asset directory using an AssetType enum"""
        self.assertEqual(self.asset.get_asset_dir_name(AssetType.THEMES), "themes")

    def test_get_asset_dir_name_with_string(self):
        """Test retrieving asset directory using a string"""
        self.assertEqual(self.asset.get_asset_dir_name("themes"), "themes")

    def test_get_asset_dir_name_invalid_string(self):
        """Test retrieving asset directory with an invalid string"""
        with self.assertRaises(ValueError) as context:
            self.asset.get_asset_dir_name("invalid")
        self.assertIn("The provided asset name", str(context.exception))

    def test_get_asset_dir_name_invalid_type(self):
        """Test retrieving asset directory with an invalid type"""
        self.assertEqual(self.asset.get_asset_dir_name(123), "")

    def test_asset_type_enum_values(self):
        """Ensure AssetType values are correct"""
        self.assertEqual(AssetType.ASSET_MIN.value, 0)
        self.assertEqual(AssetType.THEMES.value, 0)
        self.assertEqual(AssetType.ASSET_COUNT.value, 1)

    def test_file_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subfolder inside the temporary directory
            subfolder = os.path.join(temp_dir, "data")
            os.makedirs(subfolder)
            DataDirectoryManager.STANDARD_LOCATIONS = DataDirectoryManager.STANDARD_LOCATIONS + [Path(subfolder)]
            assets = StandardAssets().get()
            for asset in assets:
                asset_dir = os.path.join(subfolder, asset)
                os.makedirs(asset_dir)

            data_dir = DataDirectoryManager.find_data_directory()
            DataDirectoryManager.validate_data_directory(data_dir, assets)

            file_manager = FileManager()
            file_manager.add_virtual_directory("data", data_dir)
            data_dir_actual = file_manager.resolve_virtual_path("data")
            data_dir_expected = Path(temp_dir) / "data/"
            self.assertEqual(data_dir_actual, data_dir_expected)

    def test_data_file_manager_discover_subdirs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subfolder inside the temporary directory
            subfolder = os.path.join(temp_dir, "data")
            os.makedirs(subfolder)
            DataDirectoryManager.STANDARD_LOCATIONS = DataDirectoryManager.STANDARD_LOCATIONS + [Path(subfolder)]
            assets = StandardAssets()
            for asset in assets.get():
                asset_dir = os.path.join(subfolder, asset)
                os.makedirs(asset_dir)
            
            actual_discovered_paths = DataDirectoryManager.discover_paths(["themes"])
            theme_dir = assets.get_asset_dir_name(AssetType.THEMES)
            expected_discovered_paths = [Path(subfolder) / theme_dir]
            self.assertEqual(expected_discovered_paths, actual_discovered_paths)


    def test_discover_theme_classic_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subfolder inside the temporary directory
            datafolder = os.path.join(temp_dir, "data/")
            os.makedirs(datafolder)
            themesfolder = os.path.join(datafolder, "themes/")
            os.makedirs(themesfolder)
            classicfolder = os.path.join(themesfolder, "classic/")
            os.makedirs(classicfolder)

            self.assertIn("data/themes/classic", str(classicfolder))
            file_manager = FileManager()
            file_manager.add_virtual_directory("/data", Path(datafolder))
            file_manager.add_virtual_directory("/data/themes", Path(themesfolder))
            file_manager.add_virtual_directory("/data/themes/classic", Path(classicfolder))
            actual_classic_theme_path = file_manager.resolve_virtual_path("/data/themes/classic")
            self.assertEqual(Path(temp_dir) / "data" / "themes" / "classic", actual_classic_theme_path)
            actual_theme_config_file_path = Path(actual_classic_theme_path) / "theme.cfg"
            # Write content to the file
            with open(actual_theme_config_file_path, "w") as config_file:
                config_file.write(classic_theme_file)
            file_manager.add_virtual_file("/data/themes/classic/theme.cfg", actual_theme_config_file_path)
            theme_file = file_manager.resolve_virtual_path("/data/themes/classic/theme.cfg")
            f = open(theme_file)
            contents = f.read()
            theme_data = tomllib.loads(contents)
            f.close()
            self.assertEqual(theme_data["name"], "classic")
            self.assertEqual(theme_data["authors"], ["Cameron Nicolson"])
            self.assertEqual(theme_data["variant"], "")
            self.assertEqual(theme_data["version"], "0.1.0")
            self.assertEqual(theme_data["license"], "BSD-1-Clause")

    def test_multiple_themes_create(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subfolder inside the temporary directory
            subfolder = os.path.join(temp_dir, "data")
            os.makedirs(subfolder)
            DataDirectoryManager.STANDARD_LOCATIONS = DataDirectoryManager.STANDARD_LOCATIONS + [Path(subfolder)]
            assets = StandardAssets()
            theme_asset_dir = assets.get_asset_dir_name(AssetType.THEMES)
            asset_dir = os.path.join(subfolder, theme_asset_dir)
            os.makedirs(asset_dir)
            
            file_manager = FileManager()
            file_manager.add_virtual_directory("/data", Path(subfolder))
            # add theme classic 
            theme_path = os.path.join(subfolder, "themes")
            file_manager.add_virtual_directory("/data/themes", Path(theme_path))

            classic_theme_path = Path(os.path.join(theme_path, "classic"))
            os.makedirs(classic_theme_path)
            file_manager.add_virtual_directory("/data/themes/classic", classic_theme_path)
            # add theme delta
            delta_theme_path = Path(os.path.join(theme_path, "delta"))
            os.makedirs(delta_theme_path) 
            file_manager.add_virtual_directory("/data/themes/delta", delta_theme_path)
            # add theme CookRecipe
            cookrecipe_theme_path = Path(os.path.join(theme_path, "CookRecipe"))
            os.makedirs(cookrecipe_theme_path) 
            file_manager.add_virtual_directory("/data/themes/CookieRecipe", cookrecipe_theme_path)
            # add some arbintary junk files in each theme 
            junk_file = Path(classic_theme_path / "meme.txt")
            junk_file.write_text("should not access me - junk!")
            file_manager.add_virtual_file("/data/themes/classic/meme.txt", junk_file)
            
            junk_file = Path(delta_theme_path / "deleteme.cfg")
            junk_file.write_text("should not access me - junk!") 
            file_manager.add_virtual_file("/data/themes/delta/deleteme.cfg", junk_file)
            expected_dirs = file_manager.list_all_directories("/data/themes", max_depth=1)
            expected_theme_dirs = ["CookRecipe", "delta", "classic"]
            actual_theme_dirs = []
            for theme in Path(theme_path).iterdir():
                actual_theme_dirs.append(theme.name)

            self.assertEqual(expected_theme_dirs, actual_theme_dirs)
            virtual_themes_dir_size = len(file_manager._mappings.children[0].children[0].children)
            self.assertEqual(virtual_themes_dir_size, 3)
            self.assertEqual(len(expected_dirs), 3) 

    def test_discover_theme_common_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subfolder inside the temporary directory
            subfolder = os.path.join(temp_dir, "data")
            os.makedirs(subfolder)
            DataDirectoryManager.STANDARD_LOCATIONS = DataDirectoryManager.STANDARD_LOCATIONS + [Path(subfolder)]
            assets = StandardAssets()
            for asset in assets.get():
                asset_dir = os.path.join(subfolder, asset)
                os.makedirs(asset_dir)
            
            file_manager = FileManager()
            data_dir = DataDirectoryManager.find_data_directory()
            file_manager.add_virtual_directory("/data", data_dir)
            data_dir_actual = file_manager.resolve_virtual_path("/data")
            data_dir_expected = Path(temp_dir) / "data/"
            self.assertEqual(data_dir_actual, data_dir_expected)
            theme_dir = assets.get_asset_dir_name(AssetType.THEMES)
            system_path_themes = Path(subfolder) / theme_dir
            file_manager.add_virtual_directory("/data/themes", system_path_themes)
            actual_resolved_themes_system_path = file_manager.resolve_virtual_path("/data/themes/")
            self.assertEqual(actual_resolved_themes_system_path,
                             system_path_themes)

            system_path_common_theme = Path(subfolder) / theme_dir / "common"
            os.makedirs(str(system_path_common_theme))
            file_manager.add_virtual_directory("data/themes/common", system_path_common_theme)
            actual_resolved_common_theme_system_path = file_manager.resolve_virtual_path("data/themes/common")
            self.assertEqual(actual_resolved_common_theme_system_path,
            system_path_common_theme)
             

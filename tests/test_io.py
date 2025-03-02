import unittest
import tempfile
import os
from enum import Enum
from blog_improved.io.standard_assets import AssetType, StandardAssets
from blog_improved.io.file_manager import FileManager
from blog_improved.io.data_directory_manager import DataDirectoryManager
from django.test import TestCase
from pathlib import Path

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

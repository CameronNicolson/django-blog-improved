import tomllib
import tempfile
from .helpers import load_fixture
from django.test import TestCase
from blog_improved.utils.math import RangeClamper
from blog_improved.themes.base.base_theme import BaseTheme
from pathlib import Path

class TestTheme(TestCase):
    def setUp(self):
        self.bootstrap_theme = BaseTheme(
            name="Bootstrap",
            width_scale = {
                8.33: "col-1",
                16.66: "col-2",
                24.99: "col-3",
                33.32: "col-4",
                41.65: "col-5",
                49.98: "col-6",
                58.31: "col-7",
                66.64: "col-8",
                74.97: "col-9",
                83.3: "col-10",
                91.63: "col-11",
                99.96: "col-12"
            })

        self.neggytheme = BaseTheme(
            name = "negative value theme",
            width_scale = {
                -100: "minus-full",
                -50: "minus-half",
                -25: "minus-quarter",
                10: "one-tenth",
                70: "seven-tenth",
                100: "full"
            },
        )
    
    def test_example_theme_valid(self):
        example_theme = load_fixture("classic_theme_example.cfg")
        self.assertIn('name = "classic"\n', example_theme)
        self.assertIn('authors = ["Cameron Nicolson"]', example_theme)
        self.assertIn('variant = ""', example_theme)
        self.assertIn('version = "0.1.0"', example_theme)
        self.assertIn('license = "BSD-1-Clause"', example_theme)

    def test_serialize_classic_theme(self):
        classic_theme = BaseTheme(name="classic", authors=["Cameron Nicolson"], variant="", version="0.1.0", source_license="BSD-1-Clause")
        example_theme_file = load_fixture("classic_theme_example.cfg")
        expected_theme_data = tomllib.loads(example_theme_file)
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "theme.cfg"
            classic_theme.save_to_file(filename)
            # Now check the file was created successfully
            self.assertTrue(filename.exists())
            self.assertTrue(filename.is_file())
            actual_theme_data = None
            with open(filename, "rb") as f:
                actual_theme_data = tomllib.load(f)
            self.assertEqual(expected_theme_data["name"],
                             actual_theme_data["name"])
            self.assertEqual(expected_theme_data["authors"],
                             actual_theme_data["authors"])
            self.assertEqual(expected_theme_data["license"],
                             actual_theme_data["license"])
            self.assertEqual(expected_theme_data["version"],
                             actual_theme_data["version"])
            self.assertEqual(expected_theme_data["grid_properties"],
                             actual_theme_data["grid_properties"])
            self.assertEqual(expected_theme_data["width_scale"],
                             actual_theme_data["width_scale"])

    def test_one_quarter(self):
        basetheme = BaseTheme()
        actual_width = basetheme.width_scale[25]
        self.assertEqual(actual_width, "3")

    def test_one_third(self): 
        basetheme = BaseTheme()
        actual_width = basetheme.width_scale[33]
        self.assertEqual(actual_width, "4")

    def test_full(self):
        basetheme = BaseTheme()
        actual_width = basetheme.width_scale[100]
        self.assertEqual(actual_width, "12")

    def test_within_offset(self):
        basetheme = BaseTheme()

        with self.assertRaises(KeyError):
            actual_width = basetheme.width_scale[11]

    def test_zero(self): 
        basetheme = BaseTheme()
        with self.assertRaises(KeyError):
            actual_width = basetheme.width_scale[0]

    def test_over(self):
        basetheme = BaseTheme()
        with self.assertRaises(KeyError):
            actual_width = basetheme.width_scale[200]


from django.test import TestCase
from blog_improved.utils.math import RangeClamper
from blog_improved.themes.base.base_theme import BaseTheme

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


from django.test import TestCase
from blog_improved.themes.base.theme import WidthNegotiator
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
            width_negotiator=WidthNegotiator(0)
        )

    def test_one_quarter(self):
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(25)
        self.assertEqual(actual_width, "one-quarter")

    def test_one_third(self): 
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(38)
        self.assertEqual(actual_width, "one-third")

    def test_full(self):
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(100)
        self.assertEqual(actual_width, "full")

    def test_within_offset(self):
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(11)
        self.assertEqual(actual_width, "one-quarter")

    def test_zero(self): 
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(0)
        self.assertEqual(actual_width, None)

    def test_over(self):
        basetheme = BaseTheme()
        actual_width = basetheme.find_width(200)
        self.assertEqual(actual_width, None)

    def test_none_type(self):
        basetheme = BaseTheme()
        expected = ValueError
        self.assertRaises(expected, basetheme.find_width, None)

    def test_negative_integer(self):
        theme = self.neggytheme
        actual_width = theme.find_width(-20)
        self.assertEqual(actual_width, "minus-quarter")

    def test_negative_scale(self):
        theme = self.neggytheme
        actual_width = theme.find_width(-50)
        self.assertEqual(actual_width, "minus-half")

    def test_negative_scale_again(self):
        theme = self.neggytheme
        actual_width = theme.find_width(0)
        self.assertEqual(actual_width, "minus-quarter")

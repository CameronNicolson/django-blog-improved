from django.test import TestCase
from blog_improved.utils import strings as StringUtils

class TestStringUtils(TestCase):
    def test_split_string_non_default_deliminter(self):
        actual = StringUtils.split_string("have:a:great:day", ":")
        expected = ["have", "a", "great", "day"]
        self.assertEqual(actual, expected)

    def test_split_string_empty_elements(self):
        actual = StringUtils.split_string(" , , , ", ",")
        expected = []
        expected_num_of_elems = 0
        actual_num_of_elems = len(actual)
        self.assertEqual(actual_num_of_elems, actual_num_of_elems)

    def test_split_string_deliminter_arg_omitted(self):
        actual = StringUtils.split_string("space,cowboy")
        expected = ["space","cowboy"] 
        self.assertEqual(actual, expected)

    def test_split_string_empty_input_string_arg(self):
        actual = StringUtils.split_string("")
        expected = []
        self.assertEqual(actual, expected)

    def test_split_string_no_lead_trailing_whitespace(self):
        actual = StringUtils.split_string(" berlin,tokyo , london , paris , new york ")
        expected = ["berlin", "tokyo", "london", "paris", "new york"]
        self.assertEqual(actual, expected)

    # convert_str_kwargs_to_list tests

class ConvertStrKwargsToListTests(TestCase):

    def test_single_string_argument(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1="apple,banana,cherry")
        self.assertEqual(result['arg1'], ['apple', 'banana', 'cherry'])

    def test_multiple_string_arguments(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1="apple,banana,cherry", arg2="foo, bar , baz")
        self.assertEqual(result['arg1'], ['apple', 'banana', 'cherry'])
        self.assertEqual(result['arg2'], ['foo', 'bar', 'baz'])

    def test_non_string_argument(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1="apple,banana,cherry", arg2=42)
        self.assertEqual(result['arg1'], ['apple', 'banana', 'cherry'])
        self.assertEqual(result['arg2'], 42)

    def test_mixed_arguments(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1="apple,banana,cherry", arg2="foo, bar , baz", arg3=42)
        self.assertEqual(result['arg1'], ['apple', 'banana', 'cherry'])
        self.assertEqual(result['arg2'], ['foo', 'bar', 'baz'])
        self.assertEqual(result['arg3'], 42)

    def test_empty_string_argument(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1="")
        self.assertEqual(result['arg1'], [])

    def test_no_string_arguments(self):
        @StringUtils.convert_str_kwargs_to_list
        def test_function(**kwargs):
            return kwargs

        result = test_function(arg1=42, arg2=3.14)
        self.assertEqual(result['arg1'], 42)
        self.assertEqual(result['arg2'], 3.14)

from django.test import TestCase
from blog_improved.utils.matrices import process_layout,calc_layout_metrics, create_matrix, LayoutMetrics, ProcessedLayout

class TestProcessLayout(TestCase):
    def test_ascending_four_column_integer(self): 
        data = (4,13,243,5435,)
        expected_layout = [4,13,243,5435,]
        expected_max_val = 5435
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_descending_four_column_integer(self): 
        data = (999999,79471,2222,1,)
        expected_layout = [999999,79471,2222,1,]
        expected_max_val = 999999
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_all_false_bool(self): 
        data = (False,False,False,False,)
        expected_layout = [0,0,0,0,]
        expected_max_val = 0
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_all_true_bool(self): 
        data = (True,True,True,True,)
        expected_layout = [1,1,1,1,]
        expected_max_val = 1
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_mixed_true_false_bool(self): 
        data = (False,True,True,False,)
        expected_layout = [0,1,1,0,]
        expected_max_val = 1
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_repeating_column_multi_type(self): 
        data = (59,True,11,True)
        expected_layout = [59,59,11,59,]
        expected_max_val = 59
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

    def test_maximum_int_middle_column_true_false_bool(self): 
        data = (True,10,False,)
        expected_layout = [10,10,0,]
        expected_max_val = 10
        actual_layout = process_layout(data)
        self.assertEqual(expected_layout, actual_layout.values)
        self.assertEqual(expected_max_val, actual_layout.max_value)

class TestLayoutMetrics(TestCase):
    def test_full_symetrical_layout_metrics(self):
        data = ProcessedLayout([5,5,5,5,5], 5)
        actual_metrics = calc_layout_metrics(data)
        self.assertEqual(actual_metrics.columns, 5)
        self.assertEqual(actual_metrics.rows, 5)
        self.assertEqual(actual_metrics.entries, 25)

    def test_gapped_layout_metrics(self):
        data = ProcessedLayout([10,0,10,0], 10)
        actual_metrics = calc_layout_metrics(data)
        self.assertEqual(actual_metrics.columns, 4)
        self.assertEqual(actual_metrics.rows, 10)
        self.assertEqual(actual_metrics.entries, 20)

    def test_gapped_layout_metrics(self):
        data = ProcessedLayout([0,0], 0)
        actual_metrics = calc_layout_metrics(data)
        self.assertEqual(actual_metrics.columns, 0)
        self.assertEqual(actual_metrics.rows, 0)
        self.assertEqual(actual_metrics.entries, 0)

    def test_no_value_param(self):
        data = None
        actual_metrics = calc_layout_metrics(data)
        self.assertEqual(actual_metrics.columns, 0)
        self.assertEqual(actual_metrics.rows, 0)
        self.assertEqual(actual_metrics.entries, 0)


class TestHtmlGenerator(TestCase):
    def test_horizontal_post_list(self):
        # Post 1    Post 2    Post 3
        #           Post 4    Post 5
        #           Post 6    Post 7
        #           Post 8    Post 9
        #                     Post 10
        #                     Post 11
        
        data = [1,2,3,None,4,5,None,6,7,None,8,9,
                None,None,10,None,None,11]
        metrics = LayoutMetrics(
                columns=3,
                rows=6,
                entries=11
        )

        expected_matrix = [
                [1,2,3],
                [None,4,5],
                [None,6,7],
                [None,8,9],
                [None,None,10],
                [None,None,11],
        ]
        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)

    def test_horizontal_first_column_longest(self):
        # Post 1    Post 2    Post 3
        # Post 4    Post 5    Post 6
        # Post 7
        # Post 8
        # Post 9

        data = [1,2,3,4,5,6,7,None,None,8,None,None,9,None,None]
        metrics = LayoutMetrics(
                columns=3,
                rows=5,
                entries=9
        )
        expected_matrix = [
                [1,2,3],
                [4,5,6],
                [7,None,None],
                [8,None,None],
                [9,None,None],
        ]
        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)

    def test_single_row(self):
        # Post 1    Post 2    Post 3    Post 4 
        data =[1,2,3,4]
        metrics = LayoutMetrics(
                columns=4,
                rows=1,
                entries=4
        )

        expected_matrix = [
                [1,2,3,4],
        ]
        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)


    def test_single_column(self):
        # Post 1
        # Post 2
        # Post 3
        # ...
        # Post 17

        data = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        self.assertEqual(len(data), 17)
        metrics = LayoutMetrics(
                columns=1,
                rows=17,
                entries=17
        )

        expected_matrix = [
                [1],[2],[3],[4],[5],[6],[7],[8],[9],
                [10],[11],[12],[13],[14],[15],[16],
                [17]
                ]
        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)

    def test_none_data(self):
        data = []
        expected_matrix = [] #empty
        metrics = LayoutMetrics(
                columns=112,
                rows=63,
                entries=55
        )
        expected = IndexError
        self.assertRaises(expected, create_matrix, data, metrics)

    def test_longest_middle_column(self):
        # Post 1    Post 2    Post 3    Post 4   Post 5
        # Post 6    Post 7    Post 8    Post 9   Post 10
        #                     Post 11
        #                     Post 12

        data = [1,2,3,4,5,6,7,8,9,10,None,None,11,None,None,None,None,12,None,None]
        metrics = LayoutMetrics(
                columns=5,
                rows=4,
                entries=12
        )
        expected_matrix = [
                        [1,2,3,4,5],
                        [6,7,8,9,10],
                        [None,None,11,None,None],
                        [None,None,12,None,None]
                ]
        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)

    def test_string_dataset_success(self):
        data = ["the", "quick", "brown", "fox", 
                "jumps", "over", "the", "lazy", "dog"]
        expected_matrix = [ 
                           ["the", "quick", "brown"],
                           ["fox", "jumps", "over"],
                           ["the", "lazy", "dog",]
                           ]
        metrics = LayoutMetrics(
                columns=3,
                rows=3,
                entries=9
        )

        actual_matrix = create_matrix(data, metrics)
        self.assertEqual(expected_matrix, actual_matrix)


SupportedNumbers = (int, float, complex,)
def find_width(scale, value):
    if not isinstance(value, SupportedNumbers):
        raise ValueError("Expects a number type")
    prev = None
    for i, width in enumerate(scale):
        if i == 0:
            prev = width
        if value == width:
            return width 
        elif value >= prev and value < width:
            return prev
        prev = width
    return None



from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Iterator, NamedTuple

# Top-level function to call __has_next__ on an iterable
def hasnext(iterable, next_type=None):
    if hasattr(iterable, '__has_next__'):
        return iterable.__has_next__(next_type)
    raise TypeError(f"Object of type {type(iterable).__name__} does not support hasnext")


@dataclass
class LayoutMetrics:
    columns: int
    rows: int
    entries: int

@dataclass
class ProcessedLayout:
    values: list[int]
    max_value: int

class TraversalType(Enum):
    NONE = 0
    ROW = 1
    COLUMN = 2
    ROW_AND_COLUMN = 3

class MatrixIterator(Iterator):
    def __init__(self, matrix: List[List[Any]]):
        self._matrix = matrix
        self._curr_row = 0
        self._curr_column = 0

    def __iter__(self):
        self._curr_row = 0
        self._curr_column = 0
        return self

    def _advance(self):
        """Advance to the next element."""
        self._curr_column += 1
        if self._curr_column >= len(self._matrix[self._curr_row]):
            self._curr_column = 0
            self._curr_row += 1

    def __next__(self):
        if not self.__has_next__(TraversalType.ROW_AND_COLUMN):
            raise StopIteration()
        value = self._matrix[self._curr_row][self._curr_column]
        self._advance()  # Move to the next position
        return value

    def __has_next__(self, next_type=TraversalType.ROW_AND_COLUMN):
        """Check if there is a next element based on traversal type."""
        if next_type == TraversalType.ROW:
            # Check if there are more rows to traverse
            return self._curr_row + 1 < len(self._matrix)
        elif next_type == TraversalType.COLUMN:
            # Check if there are more columns in the current row
            return (self._curr_column + 1) < len(self._matrix[self._curr_row])
        elif next_type == TraversalType.ROW_AND_COLUMN:
            # Check if there's another element in any direction
            return (
                self._curr_row < len(self._matrix) and
                self._curr_column < len(self._matrix[self._curr_row])
            )
        return False
 
class RowIterator:
    def __init__(self, matrix: List[List[int]]):
        self.matrix = matrix
        self.row = 0
        self.col = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.row >= len(self.matrix):
            raise StopIteration

        value = self.matrix[self.row][self.col]
        if self.col + 1 < len(self.matrix[self.row]):
            self.col += 1
        else:
            self.row += 1
            self.col = 0

        return value


class ColumnIterator:
    def __init__(self, matrix: List[List[int]]):
        self.matrix = matrix
        self.row = 0
        self.col = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.col >= len(self.matrix[0]):
            raise StopIteration

        value = self.matrix[self.row][self.col]
        if self.row + 1 < len(self.matrix):
            self.row += 1
        else:
            self.row = 0
            self.col += 1

        return value

class Matrix(list):
    def __init__(self, initial_data:list, rows=None, columns=None, iterator:Iterator=MatrixIterator, traverse:int=3):
        super().__init__(initial_data)
        if rows is None or columns is None:
            raise ValueError()
        self._rows = rows
        self._columns = columns
        self._iter = iterator
        self._traversal_type = traverse

    def __iter__(self):
        return self._iter(self)
   
    def append(self, value):
        current_row = len(self)
        if current_row > self._rows:
            return IndexError("Out of bounds")

        if not self:
            super().insert(0, [])
        current_col = len(self[-1])
        if current_col >= self._columns:
            super().append([])
            current_row += 1
            current_col = 0
        self[current_row-1].append(value)

def process_layout(layout: tuple) -> ProcessedLayout:
    """
    Transform a layout tuple with various types into strictly numbers. For example, converting booleans to integers based on max value.
    e.g. input  -> (False, 29, True, False, 2,)
         output -> (0, 29, 29, 0, 2,)
    Args:
        layout: Tuple of integers or booleans like (10,5,4) or (True,False,2)
    Returns:
        ProcessedLayout: Processed values and the maximum integer value
    """
    if not layout:
        return ProcessedLayout([], 0)
    
    # Get max value from integers only once
    max_value = max(v for v in layout if isinstance(v, int))
    
    # Convert boolean values to integers using the max_value
	# When boolean and value is valid:
	# True will be converted to the maximum integer
	# False will be converted to 0
    processed_values = [
        max_value if isinstance(v, bool) and v 
        else 0 if isinstance(v, bool) 
        else v 
        for v in layout
    ]
    
    return ProcessedLayout(processed_values, max_value)


def calc_layout_metrics(data: tuple) -> LayoutMetrics:
    if not data:
        return LayoutMetrics(0,0,0)

    num_columns = len(data.values)
    num_rows = data.max_value
    if num_rows <= 0:
        return LayoutMetrics(0,0,0)

    def _sum(value:int, container:list, index=0):
        index = index
        if index >= len(container):
            return value

        curr_value = value
        next_value = container[index]
        result = curr_value + next_value
        return _sum(result, container, index + 1)

    total_entries = _sum(0, data.values)

    return LayoutMetrics(
        columns=num_columns,
        rows=num_rows,
        entries=total_entries
    )

def round_down(numerator, denominator):
    if numerator == 0 and denominator == 0:
        return 0
    d, m = divmod(numerator, denominator)
    return int(d)

def create_matrix(data:list, metrics: LayoutMetrics, step=0) -> list[int]:
    max_size = (metrics.columns * metrics.rows)
    start_step = step
    matrix = list()

    def _build_matrix(step, 
                max_size, columns, rows, 
                matrix, data):
        if step == max_size:
            return matrix
        row = round_down(step, columns)
        column = step - (row * columns)

        # is first column of row ?
        if step % columns == 0:
         	matrix.append([
                None for _ in range(columns)
            ])
        value = data[step]
        matrix[row][column] = value
        return _build_matrix(step + 1, max_size, columns, rows, matrix, data)

    matrix_data = _build_matrix(start_step, max_size, metrics.columns, metrics.rows, matrix, data)
    return Matrix(matrix_data, metrics.columns, metrics.rows)


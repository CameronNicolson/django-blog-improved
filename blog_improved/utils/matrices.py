from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class LayoutMetrics:
    columns: int
    rows: int
    entries: int

@dataclass
class ProcessedLayout:
    values: list[int]
    max_value: int

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

def create_matrix(layout: tuple, process_layout=process_layout, step=0) -> list[int]:
    strict_layout = process_layout(layout) 
    metrics = calc_layout_metrics(strict_layout)
    max_size = (metrics.columns * metrics.rows)
    start_step = step
    matrix = list()

    def _build_matrix(step, 
                max_size, columns, rows, 
                matrix, strict_layout, index):
        if step == max_size:
            return matrix
        row = round_down(step, columns)
        column = step - (row * columns)

        # is first column of row ?
        if step % columns == 0:
         	matrix.append([
                None for _ in range(columns)
            ])
        if (row < strict_layout.values[column]):
            value = index
            matrix[row][column] = value
            index = index + 1
        return _build_matrix(step + 1, max_size, columns, rows, matrix, strict_layout, index)

    return _build_matrix(start_step, max_size, metrics.columns, metrics.rows, matrix, strict_layout, 1)


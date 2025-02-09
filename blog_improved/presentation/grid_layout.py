from dataclasses import dataclass
from .layout import Layout

@dataclass
class GridLayout(Layout):
    rows: int = 0
    columns: int = 0
    column_width: set[int] = None
    row_width: set[int] = None

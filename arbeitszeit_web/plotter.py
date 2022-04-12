from datetime import datetime
from decimal import Decimal
from typing import List, Protocol, Tuple


class Plotter(Protocol):
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], fig_size: Tuple[int, int] = (10, 5)
    ) -> str:
        ...

from datetime import datetime
from decimal import Decimal
from typing import List, Tuple


class FakePlotter:
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], size: Tuple[int, int] = (10, 5)
    ) -> str:
        return "fake_plot"

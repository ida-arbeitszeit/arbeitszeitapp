from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Union


class FakePlotter:
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], fig_size: Tuple[int, int] = (10, 5)
    ) -> str:
        return "fake line plot"

    def create_bar_plot(
        self,
        x_coordinates: List[Union[int, str]],
        height_of_bars: List[Decimal],
        colors_of_bars: List[str],
        fig_size: Tuple[int, int],
        y_label: Optional[str] = None,
    ) -> str:
        return "fake bar plot"

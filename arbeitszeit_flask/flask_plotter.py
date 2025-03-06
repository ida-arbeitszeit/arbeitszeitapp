import io
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Union

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class FlaskPlotter:
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], fig_size: Tuple[int, int] = (10, 5)
    ) -> bytes:
        fig = Figure()
        ax = fig.subplots()
        ax.axhline(linestyle="--", color="black")
        ax.plot(x, y)  # type: ignore[arg-type]
        fig.set_size_inches(fig_size[0], fig_size[1])
        return self._figure_to_bytes(fig)

    def create_bar_plot(
        self,
        x_coordinates: List[Union[int, str]],
        height_of_bars: List[Decimal],
        colors_of_bars: List[str],
        fig_size: Tuple[int, int],
        y_label: Optional[str],
    ) -> bytes:
        fig = Figure()
        ax = fig.subplots()
        ax.bar(x_coordinates, height_of_bars, color=colors_of_bars)  # type: ignore[arg-type]
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if y_label:
            ax.set_ylabel(y_label)
        fig.set_size_inches(fig_size[0], fig_size[1])
        return self._figure_to_bytes(fig)

    def _figure_to_bytes(self, fig: Figure) -> bytes:
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output.getvalue()

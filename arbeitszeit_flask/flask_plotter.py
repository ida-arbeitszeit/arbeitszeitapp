import base64
import io
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from matplotlib.figure import Figure


class FlaskPlotter:
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], fig_size: Tuple[int, int] = (10, 5)
    ) -> str:
        fig = Figure()
        ax = fig.subplots()
        ax.axhline(linestyle="--", color="black")
        ax.plot(x, y)
        fig.set_size_inches(fig_size[0], fig_size[1])
        return self._fig_to_string(fig)

    def _fig_to_string(self, fig: Figure) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        string = base64.b64encode(buf.getbuffer()).decode("utf-8")
        return string

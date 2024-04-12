from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib._tight_bbox import (
    process_figure_for_rasterizing as process_figure_for_rasterizing,
)

from .backend_agg import RendererAgg as RendererAgg

class MixedModeRenderer:
    dpi: Incomplete
    figure: Incomplete
    def __init__(
        self,
        figure,
        width,
        height,
        dpi,
        vector_renderer,
        raster_renderer_class: Incomplete | None = None,
        bbox_inches_restore: Incomplete | None = None,
    ) -> None: ...
    def __getattr__(self, attr): ...
    def start_rasterizing(self) -> None: ...
    def stop_rasterizing(self) -> None: ...

from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.backend_bases import FigureCanvasBase as FigureCanvasBase
from matplotlib.backend_bases import FigureManagerBase as FigureManagerBase
from matplotlib.backend_bases import RendererBase as RendererBase
from matplotlib.backend_bases import _Backend
from matplotlib.font_manager import get_font as get_font
from matplotlib.ft2font import LOAD_DEFAULT as LOAD_DEFAULT
from matplotlib.ft2font import LOAD_FORCE_AUTOHINT as LOAD_FORCE_AUTOHINT
from matplotlib.ft2font import LOAD_NO_AUTOHINT as LOAD_NO_AUTOHINT
from matplotlib.ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING
from matplotlib.mathtext import MathTextParser as MathTextParser
from matplotlib.path import Path as Path
from matplotlib.transforms import Bbox as Bbox
from matplotlib.transforms import BboxBase as BboxBase

def get_hinting_flag(): ...

class RendererAgg(RendererBase):
    dpi: Incomplete
    width: Incomplete
    height: Incomplete
    mathtext_parser: Incomplete
    bbox: Incomplete
    def __init__(self, width, height, dpi) -> None: ...
    def draw_path(
        self, gc, path, transform, rgbFace: Incomplete | None = None
    ) -> None: ...
    def draw_mathtext(self, gc, x, y, s, prop, angle) -> None: ...
    def draw_text(
        self,
        gc,
        x,
        y,
        s,
        prop,
        angle,
        ismath: bool = False,
        mtext: Incomplete | None = None,
    ): ...
    def get_text_width_height_descent(self, s, prop, ismath): ...
    def draw_tex(
        self, gc, x, y, s, prop, angle, *, mtext: Incomplete | None = None
    ) -> None: ...
    def get_canvas_width_height(self): ...
    def points_to_pixels(self, points): ...
    def buffer_rgba(self): ...
    def tostring_argb(self): ...
    def tostring_rgb(self): ...
    def clear(self) -> None: ...
    def option_image_nocomposite(self): ...
    def option_scale_image(self): ...
    def restore_region(
        self, region, bbox: Incomplete | None = None, xy: Incomplete | None = None
    ) -> None: ...
    def start_filter(self) -> None: ...
    def stop_filter(self, post_processing) -> None: ...

class FigureCanvasAgg(FigureCanvasBase):
    def copy_from_bbox(self, bbox): ...
    def restore_region(
        self, region, bbox: Incomplete | None = None, xy: Incomplete | None = None
    ): ...
    renderer: Incomplete
    def draw(self) -> None: ...
    def get_renderer(self): ...
    def tostring_rgb(self): ...
    def tostring_argb(self): ...
    def buffer_rgba(self): ...
    def print_raw(
        self, filename_or_obj, *, metadata: Incomplete | None = None
    ) -> None: ...
    print_rgba = print_raw
    def print_png(
        self,
        filename_or_obj,
        *,
        metadata: Incomplete | None = None,
        pil_kwargs: Incomplete | None = None,
    ) -> None: ...
    def print_to_buffer(self): ...
    def print_jpg(
        self,
        filename_or_obj,
        *,
        metadata: Incomplete | None = None,
        pil_kwargs: Incomplete | None = None,
    ) -> None: ...
    print_jpeg = print_jpg
    def print_tif(
        self,
        filename_or_obj,
        *,
        metadata: Incomplete | None = None,
        pil_kwargs: Incomplete | None = None,
    ) -> None: ...
    print_tiff = print_tif
    def print_webp(
        self,
        filename_or_obj,
        *,
        metadata: Incomplete | None = None,
        pil_kwargs: Incomplete | None = None,
    ) -> None: ...

class _BackendAgg(_Backend):
    backend_version: str
    FigureCanvas = FigureCanvasAgg
    FigureManager = FigureManagerBase

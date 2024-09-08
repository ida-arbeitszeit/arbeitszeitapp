from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.backend_bases import FigureCanvasBase as FigureCanvasBase
from matplotlib.backend_bases import FigureManagerBase as FigureManagerBase
from matplotlib.backend_bases import RendererBase as RendererBase
from matplotlib.backend_bases import _Backend
from matplotlib.backends.backend_mixed import MixedModeRenderer as MixedModeRenderer
from matplotlib.colors import rgb2hex as rgb2hex
from matplotlib.dates import UTC as UTC
from matplotlib.path import Path as Path
from matplotlib.transforms import Affine2D as Affine2D
from matplotlib.transforms import Affine2DBase as Affine2DBase

class XMLWriter:
    def __init__(self, file) -> None: ...
    def start(self, tag, attrib={}, **extra): ...
    def comment(self, comment) -> None: ...
    def data(self, text) -> None: ...
    def end(self, tag: Incomplete | None = None, indent: bool = True) -> None: ...
    def close(self, id) -> None: ...
    def element(
        self, tag, text: Incomplete | None = None, attrib={}, **extra
    ) -> None: ...
    def flush(self) -> None: ...

class RendererSVG(RendererBase):
    width: Incomplete
    height: Incomplete
    writer: Incomplete
    image_dpi: Incomplete
    basename: Incomplete
    def __init__(
        self,
        width,
        height,
        svgwriter,
        basename: Incomplete | None = None,
        image_dpi: int = 72,
        *,
        metadata: Incomplete | None = None,
    ) -> None: ...
    def finalize(self) -> None: ...
    def open_group(self, s, gid: Incomplete | None = None) -> None: ...
    def close_group(self, s) -> None: ...
    def option_image_nocomposite(self): ...
    def draw_path(
        self, gc, path, transform, rgbFace: Incomplete | None = None
    ) -> None: ...
    def draw_markers(
        self,
        gc,
        marker_path,
        marker_trans,
        path,
        trans,
        rgbFace: Incomplete | None = None,
    ) -> None: ...
    def draw_path_collection(
        self,
        gc,
        master_transform,
        paths,
        all_transforms,
        offsets,
        offset_trans,
        facecolors,
        edgecolors,
        linewidths,
        linestyles,
        antialiaseds,
        urls,
        offset_position,
    ): ...
    def draw_gouraud_triangles(
        self, gc, triangles_array, colors_array, transform
    ) -> None: ...
    def option_scale_image(self): ...
    def get_image_magnification(self): ...
    def draw_image(self, gc, x, y, im, transform: Incomplete | None = None) -> None: ...
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
    ) -> None: ...
    def flipy(self): ...
    def get_canvas_width_height(self): ...
    def get_text_width_height_descent(self, s, prop, ismath): ...

class FigureCanvasSVG(FigureCanvasBase):
    filetypes: Incomplete
    fixed_dpi: int
    def print_svg(
        self,
        filename,
        *,
        bbox_inches_restore: Incomplete | None = None,
        metadata: Incomplete | None = None,
    ) -> None: ...
    def print_svgz(self, filename, **kwargs): ...
    def get_default_filetype(self): ...
    def draw(self): ...

FigureManagerSVG = FigureManagerBase
svgProlog: str

class _BackendSVG(_Backend):
    backend_version: Incomplete
    FigureCanvas = FigureCanvasSVG

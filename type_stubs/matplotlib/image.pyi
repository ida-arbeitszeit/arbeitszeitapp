import matplotlib.artist as martist
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import cm as cm
from matplotlib._image import *
from matplotlib.backend_bases import FigureCanvasBase as FigureCanvasBase
from matplotlib.transforms import Affine2D as Affine2D
from matplotlib.transforms import Bbox as Bbox
from matplotlib.transforms import BboxBase as BboxBase
from matplotlib.transforms import BboxTransform as BboxTransform
from matplotlib.transforms import BboxTransformTo as BboxTransformTo
from matplotlib.transforms import IdentityTransform as IdentityTransform
from matplotlib.transforms import TransformedBbox as TransformedBbox

interpolations_names: Incomplete

def composite_images(images, renderer, magnification: float = 1.0): ...

class _ImageBase(martist.Artist, cm.ScalarMappable):
    zorder: int
    origin: Incomplete
    axes: Incomplete
    def __init__(
        self,
        ax,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        interpolation: Incomplete | None = None,
        origin: Incomplete | None = None,
        filternorm: bool = True,
        filterrad: float = 4.0,
        resample: bool = False,
        *,
        interpolation_stage: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_size(self): ...
    def get_shape(self): ...
    def set_alpha(self, alpha) -> None: ...
    def changed(self) -> None: ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ) -> None: ...
    stale: bool
    def draw(self, renderer, *args, **kwargs) -> None: ...
    def contains(self, mouseevent): ...
    def write_png(self, fname) -> None: ...
    def set_data(self, A) -> None: ...
    def set_array(self, A) -> None: ...
    def get_interpolation(self): ...
    def set_interpolation(self, s) -> None: ...
    def set_interpolation_stage(self, s) -> None: ...
    def can_composite(self): ...
    def set_resample(self, v) -> None: ...
    def get_resample(self): ...
    def set_filternorm(self, filternorm) -> None: ...
    def get_filternorm(self): ...
    def set_filterrad(self, filterrad) -> None: ...
    def get_filterrad(self): ...

class AxesImage(_ImageBase):
    def __init__(
        self,
        ax,
        *,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        interpolation: Incomplete | None = None,
        origin: Incomplete | None = None,
        extent: Incomplete | None = None,
        filternorm: bool = True,
        filterrad: float = 4.0,
        resample: bool = False,
        interpolation_stage: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ): ...
    stale: bool
    def set_extent(self, extent, **kwargs) -> None: ...
    def get_extent(self): ...
    def get_cursor_data(self, event): ...

class NonUniformImage(AxesImage):
    mouseover: bool
    def __init__(self, ax, *, interpolation: str = "nearest", **kwargs) -> None: ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ): ...
    stale: bool
    def set_data(self, x, y, A) -> None: ...
    def set_array(self, *args) -> None: ...
    def set_interpolation(self, s) -> None: ...
    def get_extent(self): ...
    def set_filternorm(self, filternorm) -> None: ...
    def set_filterrad(self, filterrad) -> None: ...
    def set_norm(self, norm) -> None: ...
    def set_cmap(self, cmap) -> None: ...

class PcolorImage(AxesImage):
    def __init__(
        self,
        ax,
        x: Incomplete | None = None,
        y: Incomplete | None = None,
        A: Incomplete | None = None,
        *,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ): ...
    stale: bool
    def set_data(self, x, y, A) -> None: ...
    def set_array(self, *args) -> None: ...
    def get_cursor_data(self, event): ...

class FigureImage(_ImageBase):
    zorder: int
    figure: Incomplete
    ox: Incomplete
    oy: Incomplete
    magnification: float
    def __init__(
        self,
        fig,
        *,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        offsetx: int = 0,
        offsety: int = 0,
        origin: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_extent(self): ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ): ...
    stale: bool
    def set_data(self, A) -> None: ...

class BboxImage(_ImageBase):
    bbox: Incomplete
    def __init__(
        self,
        bbox,
        *,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        interpolation: Incomplete | None = None,
        origin: Incomplete | None = None,
        filternorm: bool = True,
        filterrad: float = 4.0,
        resample: bool = False,
        **kwargs,
    ) -> None: ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    def contains(self, mouseevent): ...
    def make_image(
        self, renderer, magnification: float = 1.0, unsampled: bool = False
    ): ...

def imread(fname, format: Incomplete | None = None): ...
def imsave(
    fname,
    arr,
    vmin: Incomplete | None = None,
    vmax: Incomplete | None = None,
    cmap: Incomplete | None = None,
    format: Incomplete | None = None,
    origin: Incomplete | None = None,
    dpi: int = 100,
    *,
    metadata: Incomplete | None = None,
    pil_kwargs: Incomplete | None = None,
) -> None: ...
def pil_to_array(pilImage): ...
def thumbnail(
    infile,
    thumbfile,
    scale: float = 0.1,
    interpolation: str = "bilinear",
    preview: bool = False,
): ...

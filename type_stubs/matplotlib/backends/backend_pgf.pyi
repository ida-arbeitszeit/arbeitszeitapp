from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib._pylab_helpers import Gcf as Gcf
from matplotlib.backend_bases import FigureCanvasBase as FigureCanvasBase, FigureManagerBase as FigureManagerBase, RendererBase as RendererBase, _Backend
from matplotlib.backends.backend_mixed import MixedModeRenderer as MixedModeRenderer
from matplotlib.figure import Figure as Figure
from matplotlib.path import Path as Path

class __getattr__:
    NO_ESCAPE: Incomplete
    re_mathsep: Incomplete

def get_fontspec(): ...
def get_preamble(): ...

latex_pt_to_in: Incomplete
latex_in_to_pt: Incomplete
mpl_pt_to_in: Incomplete
mpl_in_to_pt: Incomplete

def common_texification(text): ...
def writeln(fh, line): ...
def make_pdf_to_png_converter(): ...

class LatexError(Exception):
    latex_output: Incomplete
    def __init__(self, message, latex_output: str = ...) -> None: ...

class LatexManager:
    tmpdir: Incomplete
    latex: Incomplete
    def __init__(self) -> None: ...
    texcommand: Incomplete
    latex_header: Incomplete
    def get_width_height_descent(self, text, prop): ...

class RendererPgf(RendererBase):
    dpi: Incomplete
    fh: Incomplete
    figure: Incomplete
    image_counter: int
    def __init__(self, figure, fh) -> None: ...
    def draw_markers(self, gc, marker_path, marker_trans, path, trans, rgbFace: Incomplete | None = ...) -> None: ...
    def draw_path(self, gc, path, transform, rgbFace: Incomplete | None = ...) -> None: ...
    def option_scale_image(self): ...
    def option_image_nocomposite(self): ...
    def draw_image(self, gc, x, y, im, transform: Incomplete | None = ...) -> None: ...
    def draw_tex(self, gc, x, y, s, prop, angle, *, mtext: Incomplete | None = ...) -> None: ...
    def draw_text(self, gc, x, y, s, prop, angle, ismath: bool = ..., mtext: Incomplete | None = ...) -> None: ...
    def get_text_width_height_descent(self, s, prop, ismath): ...
    def flipy(self): ...
    def get_canvas_width_height(self): ...
    def points_to_pixels(self, points): ...

class FigureCanvasPgf(FigureCanvasBase):
    filetypes: Incomplete
    def get_default_filetype(self): ...
    def print_pgf(self, fname_or_fh, **kwargs) -> None: ...
    def print_pdf(self, fname_or_fh, *, metadata: Incomplete | None = ..., **kwargs) -> None: ...
    def print_png(self, fname_or_fh, **kwargs) -> None: ...
    def get_renderer(self): ...
    def draw(self): ...
FigureManagerPgf = FigureManagerBase

class _BackendPgf(_Backend):
    FigureCanvas = FigureCanvasPgf

class PdfPages:
    keep_empty: Incomplete
    def __init__(self, filename, *, keep_empty: bool = ..., metadata: Incomplete | None = ...) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def close(self) -> None: ...
    def savefig(self, figure: Incomplete | None = ..., **kwargs) -> None: ...
    def get_pagecount(self): ...

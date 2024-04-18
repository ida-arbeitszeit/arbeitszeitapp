from ._backend_tk import FigureCanvasTk as FigureCanvasTk
from ._backend_tk import _BackendTk
from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_cairo import cairo as cairo

class FigureCanvasTkCairo(FigureCanvasCairo, FigureCanvasTk):
    def draw(self) -> None: ...

class _BackendTkCairo(_BackendTk):
    FigureCanvas = FigureCanvasTkCairo

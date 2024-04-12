from _typeshed import Incomplete

from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_cairo import cairo as cairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase

class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    bitmap: Incomplete
    def draw(self, drawDC: Incomplete | None = None) -> None: ...

class _BackendWxCairo(_BackendWx):
    FigureCanvas = FigureCanvasWxCairo

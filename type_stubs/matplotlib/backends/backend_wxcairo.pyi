from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo, cairo as cairo
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from _typeshed import Incomplete

class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    bitmap: Incomplete
    def draw(self, drawDC: Incomplete | None = ...) -> None: ...

class _BackendWxCairo(_BackendWx):
    FigureCanvas = FigureCanvasWxCairo

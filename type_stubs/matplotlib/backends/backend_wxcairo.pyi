from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo, cairo as cairo
from .backend_wx import FigureFrameWx as FigureFrameWx, _BackendWx, _FigureCanvasWxBase
from _typeshed import Incomplete

class FigureFrameWxCairo(FigureFrameWx):
    def get_canvas(self, fig): ...

class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    bitmap: Incomplete
    def draw(self, drawDC: Incomplete | None = ...) -> None: ...

class _BackendWxCairo(_BackendWx):
    FigureCanvas = FigureCanvasWxCairo

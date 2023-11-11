from .backend_agg import FigureCanvasAgg as FigureCanvasAgg
from .backend_wx import _BackendWx, _FigureCanvasWxBase
from _typeshed import Incomplete

class FigureCanvasWxAgg(FigureCanvasAgg, _FigureCanvasWxBase):
    bitmap: Incomplete
    def draw(self, drawDC: Incomplete | None = ...) -> None: ...
    def blit(self, bbox: Incomplete | None = ...) -> None: ...

class _BackendWxAgg(_BackendWx):
    FigureCanvas = FigureCanvasWxAgg

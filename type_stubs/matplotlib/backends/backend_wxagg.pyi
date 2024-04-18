from _typeshed import Incomplete

from .backend_agg import FigureCanvasAgg as FigureCanvasAgg
from .backend_wx import _BackendWx, _FigureCanvasWxBase

class FigureCanvasWxAgg(FigureCanvasAgg, _FigureCanvasWxBase):
    bitmap: Incomplete
    def draw(self, drawDC: Incomplete | None = None) -> None: ...
    def blit(self, bbox: Incomplete | None = None) -> None: ...

class _BackendWxAgg(_BackendWx):
    FigureCanvas = FigureCanvasWxAgg

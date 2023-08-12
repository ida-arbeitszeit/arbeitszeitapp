from ._backend_tk import FigureCanvasTk as FigureCanvasTk, FigureManagerTk as FigureManagerTk, NavigationToolbar2Tk as NavigationToolbar2Tk, _BackendTk
from .backend_agg import FigureCanvasAgg as FigureCanvasAgg
from _typeshed import Incomplete

class FigureCanvasTkAgg(FigureCanvasAgg, FigureCanvasTk):
    def draw(self) -> None: ...
    def blit(self, bbox: Incomplete | None = ...) -> None: ...

class _BackendTkAgg(_BackendTk):
    FigureCanvas = FigureCanvasTkAgg

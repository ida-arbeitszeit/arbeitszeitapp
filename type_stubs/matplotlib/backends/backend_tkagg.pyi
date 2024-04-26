from _typeshed import Incomplete

from ._backend_tk import FigureCanvasTk as FigureCanvasTk
from ._backend_tk import FigureManagerTk as FigureManagerTk
from ._backend_tk import NavigationToolbar2Tk as NavigationToolbar2Tk
from ._backend_tk import _BackendTk
from .backend_agg import FigureCanvasAgg as FigureCanvasAgg

class FigureCanvasTkAgg(FigureCanvasAgg, FigureCanvasTk):
    def draw(self) -> None: ...
    def blit(self, bbox: Incomplete | None = None) -> None: ...

class _BackendTkAgg(_BackendTk):
    FigureCanvas = FigureCanvasTkAgg

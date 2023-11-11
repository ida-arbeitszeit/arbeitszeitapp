from . import backend_agg as backend_agg, backend_gtk3 as backend_gtk3
from .. import cbook as cbook, transforms as transforms
from .backend_gtk3 import Gtk as Gtk, _BackendGTK3
from _typeshed import Incomplete

class FigureCanvasGTK3Agg(backend_agg.FigureCanvasAgg, backend_gtk3.FigureCanvasGTK3):
    def __init__(self, figure) -> None: ...
    def on_draw_event(self, widget, ctx): ...
    def blit(self, bbox: Incomplete | None = ...) -> None: ...

class _BackendGTK3Cairo(_BackendGTK3):
    FigureCanvas = FigureCanvasGTK3Agg

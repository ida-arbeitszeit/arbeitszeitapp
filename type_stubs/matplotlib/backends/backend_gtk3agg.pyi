from _typeshed import Incomplete

from .. import cbook as cbook
from .. import transforms as transforms
from . import backend_agg as backend_agg
from . import backend_gtk3 as backend_gtk3
from .backend_gtk3 import Gtk as Gtk
from .backend_gtk3 import _BackendGTK3

class FigureCanvasGTK3Agg(backend_agg.FigureCanvasAgg, backend_gtk3.FigureCanvasGTK3):
    def __init__(self, figure) -> None: ...
    def on_draw_event(self, widget, ctx): ...
    def blit(self, bbox: Incomplete | None = None) -> None: ...

class _BackendGTK3Cairo(_BackendGTK3):
    FigureCanvas = FigureCanvasGTK3Agg

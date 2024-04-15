from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_gtk3 import FigureCanvasGTK3 as FigureCanvasGTK3
from .backend_gtk3 import Gtk as Gtk
from .backend_gtk3 import _BackendGTK3

class FigureCanvasGTK3Cairo(FigureCanvasCairo, FigureCanvasGTK3):
    def on_draw_event(self, widget, ctx) -> None: ...

class _BackendGTK3Cairo(_BackendGTK3):
    FigureCanvas = FigureCanvasGTK3Cairo

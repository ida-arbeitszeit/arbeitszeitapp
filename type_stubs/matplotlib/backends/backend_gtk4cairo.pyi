from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_gtk4 import FigureCanvasGTK4 as FigureCanvasGTK4
from .backend_gtk4 import GLib as GLib
from .backend_gtk4 import Gtk as Gtk
from .backend_gtk4 import _BackendGTK4

class FigureCanvasGTK4Cairo(FigureCanvasCairo, FigureCanvasGTK4):
    def on_draw_event(self, widget, ctx) -> None: ...

class _BackendGTK4Cairo(_BackendGTK4):
    FigureCanvas = FigureCanvasGTK4Cairo

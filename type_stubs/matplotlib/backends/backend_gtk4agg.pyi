from . import backend_agg as backend_agg, backend_gtk4 as backend_gtk4
from .. import cbook as cbook
from .backend_gtk4 import Gtk as Gtk, _BackendGTK4

class FigureCanvasGTK4Agg(backend_agg.FigureCanvasAgg, backend_gtk4.FigureCanvasGTK4):
    def on_draw_event(self, widget, ctx): ...

class FigureManagerGTK4Agg(backend_gtk4.FigureManagerGTK4): ...

class _BackendGTK4Agg(_BackendGTK4):
    FigureCanvas = FigureCanvasGTK4Agg

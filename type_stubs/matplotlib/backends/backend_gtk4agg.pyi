from .. import cbook as cbook
from . import backend_agg as backend_agg
from . import backend_gtk4 as backend_gtk4
from .backend_gtk4 import GLib as GLib
from .backend_gtk4 import Gtk as Gtk
from .backend_gtk4 import _BackendGTK4

class FigureCanvasGTK4Agg(backend_agg.FigureCanvasAgg, backend_gtk4.FigureCanvasGTK4):
    def on_draw_event(self, widget, ctx): ...

class _BackendGTK4Agg(_BackendGTK4):
    FigureCanvas = FigureCanvasGTK4Agg

from .backend_agg import FigureCanvasAgg as FigureCanvasAgg
from .backend_qt import FigureCanvasQT as FigureCanvasQT, FigureManagerQT as FigureManagerQT, NavigationToolbar2QT as NavigationToolbar2QT, QtCore as QtCore, QtGui as QtGui, _BackendQT
from .qt_compat import QT_API as QT_API
from matplotlib.transforms import Bbox as Bbox

class FigureCanvasQTAgg(FigureCanvasAgg, FigureCanvasQT):
    def paintEvent(self, event) -> None: ...
    def print_figure(self, *args, **kwargs) -> None: ...

class _BackendQTAgg(_BackendQT):
    FigureCanvas = FigureCanvasQTAgg

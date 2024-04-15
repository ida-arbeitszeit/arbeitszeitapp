from matplotlib.transforms import Bbox as Bbox

from .backend_agg import FigureCanvasAgg as FigureCanvasAgg
from .backend_qt import FigureCanvasQT as FigureCanvasQT
from .backend_qt import FigureManagerQT as FigureManagerQT
from .backend_qt import NavigationToolbar2QT as NavigationToolbar2QT
from .backend_qt import _BackendQT
from .qt_compat import QT_API as QT_API
from .qt_compat import QtCore as QtCore
from .qt_compat import QtGui as QtGui

class FigureCanvasQTAgg(FigureCanvasAgg, FigureCanvasQT):
    def paintEvent(self, event) -> None: ...
    def print_figure(self, *args, **kwargs) -> None: ...

class _BackendQTAgg(_BackendQT):
    FigureCanvas = FigureCanvasQTAgg

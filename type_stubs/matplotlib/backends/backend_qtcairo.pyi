from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_cairo import cairo as cairo
from .backend_qt import FigureCanvasQT as FigureCanvasQT
from .backend_qt import _BackendQT
from .qt_compat import QT_API as QT_API
from .qt_compat import QtCore as QtCore
from .qt_compat import QtGui as QtGui

class FigureCanvasQTCairo(FigureCanvasCairo, FigureCanvasQT):
    def draw(self) -> None: ...
    def paintEvent(self, event) -> None: ...

class _BackendQTCairo(_BackendQT):
    FigureCanvas = FigureCanvasQTCairo

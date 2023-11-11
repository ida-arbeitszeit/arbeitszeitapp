from .backend_cairo import FigureCanvasCairo as FigureCanvasCairo, cairo as cairo
from .backend_qt import FigureCanvasQT as FigureCanvasQT, _BackendQT
from .qt_compat import QT_API as QT_API, QtCore as QtCore, QtGui as QtGui

class FigureCanvasQTCairo(FigureCanvasCairo, FigureCanvasQT):
    def draw(self) -> None: ...
    def paintEvent(self, event) -> None: ...

class _BackendQTCairo(_BackendQT):
    FigureCanvas = FigureCanvasQTCairo

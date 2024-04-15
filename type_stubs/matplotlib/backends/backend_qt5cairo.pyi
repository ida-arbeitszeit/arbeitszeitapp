from .. import backends as backends
from .backend_qtcairo import FigureCanvasCairo as FigureCanvasCairo
from .backend_qtcairo import FigureCanvasQT as FigureCanvasQT
from .backend_qtcairo import FigureCanvasQTCairo as FigureCanvasQTCairo
from .backend_qtcairo import _BackendQTCairo

class _BackendQT5Cairo(_BackendQTCairo): ...

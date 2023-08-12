from .. import backends as backends
from .backend_qtcairo import FigureCanvasCairo as FigureCanvasCairo, FigureCanvasQT as FigureCanvasQT, FigureCanvasQTCairo as FigureCanvasQTCairo, _BackendQTCairo

class _BackendQT5Cairo(_BackendQTCairo): ...

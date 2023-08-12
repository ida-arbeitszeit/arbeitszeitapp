from .. import backends as backends
from .backend_qtagg import FigureCanvasAgg as FigureCanvasAgg, FigureCanvasQT as FigureCanvasQT, FigureCanvasQTAgg as FigureCanvasQTAgg, FigureManagerQT as FigureManagerQT, NavigationToolbar2QT as NavigationToolbar2QT, _BackendQTAgg

class _BackendQT5Agg(_BackendQTAgg): ...

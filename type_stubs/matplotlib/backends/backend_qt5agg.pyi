from .. import backends as backends
from .backend_qtagg import FigureCanvasAgg as FigureCanvasAgg
from .backend_qtagg import FigureCanvasQT as FigureCanvasQT
from .backend_qtagg import FigureCanvasQTAgg as FigureCanvasQTAgg
from .backend_qtagg import FigureManagerQT as FigureManagerQT
from .backend_qtagg import NavigationToolbar2QT as NavigationToolbar2QT
from .backend_qtagg import _BackendQTAgg

class _BackendQT5Agg(_BackendQTAgg): ...

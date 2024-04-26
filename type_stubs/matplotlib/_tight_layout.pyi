from _typeshed import Incomplete
from matplotlib.font_manager import FontProperties as FontProperties
from matplotlib.transforms import Bbox as Bbox

def get_subplotspec_list(axes_list, grid_spec: Incomplete | None = None): ...
def get_tight_layout_figure(
    fig,
    axes_list,
    subplotspec_list,
    renderer,
    pad: float = 1.08,
    h_pad: Incomplete | None = None,
    w_pad: Incomplete | None = None,
    rect: Incomplete | None = None,
): ...

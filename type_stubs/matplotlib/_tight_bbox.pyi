from _typeshed import Incomplete
from matplotlib.transforms import Affine2D as Affine2D
from matplotlib.transforms import Bbox as Bbox
from matplotlib.transforms import TransformedBbox as TransformedBbox

def adjust_bbox(fig, bbox_inches, fixed_dpi: Incomplete | None = None): ...
def process_figure_for_rasterizing(
    fig, bbox_inches_restore, fixed_dpi: Incomplete | None = None
): ...

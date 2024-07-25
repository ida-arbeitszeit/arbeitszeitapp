from _typeshed import Incomplete

from . import backend_tools as backend_tools
from . import cbook as cbook
from . import collections as collections
from . import colors as colors
from . import ticker as ticker
from . import transforms as transforms
from .lines import Line2D as Line2D
from .patches import Ellipse as Ellipse
from .patches import Polygon as Polygon
from .patches import Rectangle as Rectangle
from .transforms import Affine2D as Affine2D
from .transforms import TransformedPatchPath as TransformedPatchPath

class LockDraw:
    def __init__(self) -> None: ...
    def __call__(self, o) -> None: ...
    def release(self, o) -> None: ...
    def available(self, o): ...
    def isowner(self, o): ...
    def locked(self): ...

class Widget:
    drawon: bool
    eventson: bool
    def set_active(self, active) -> None: ...
    def get_active(self): ...
    active: Incomplete
    def ignore(self, event): ...

class AxesWidget(Widget):
    ax: Incomplete
    canvas: Incomplete
    def __init__(self, ax) -> None: ...
    def connect_event(self, event, callback) -> None: ...
    def disconnect_events(self) -> None: ...

class Button(AxesWidget):
    label: Incomplete
    color: Incomplete
    hovercolor: Incomplete
    def __init__(
        self,
        ax,
        label,
        image: Incomplete | None = None,
        color: str = "0.85",
        hovercolor: str = "0.95",
        *,
        useblit: bool = True,
    ) -> None: ...
    def on_clicked(self, func): ...
    def disconnect(self, cid) -> None: ...

class SliderBase(AxesWidget):
    orientation: Incomplete
    closedmin: Incomplete
    closedmax: Incomplete
    valmin: Incomplete
    valmax: Incomplete
    valstep: Incomplete
    drag_active: bool
    valfmt: Incomplete
    def __init__(
        self,
        ax,
        orientation,
        closedmin,
        closedmax,
        valmin,
        valmax,
        valfmt,
        dragging,
        valstep,
    ) -> None: ...
    def disconnect(self, cid) -> None: ...
    def reset(self) -> None: ...

class Slider(SliderBase):
    slidermin: Incomplete
    slidermax: Incomplete
    val: Incomplete
    valinit: Incomplete
    track: Incomplete
    poly: Incomplete
    hline: Incomplete
    vline: Incomplete
    label: Incomplete
    valtext: Incomplete
    def __init__(
        self,
        ax,
        label,
        valmin,
        valmax,
        *,
        valinit: float = 0.5,
        valfmt: Incomplete | None = None,
        closedmin: bool = True,
        closedmax: bool = True,
        slidermin: Incomplete | None = None,
        slidermax: Incomplete | None = None,
        dragging: bool = True,
        valstep: Incomplete | None = None,
        orientation: str = "horizontal",
        initcolor: str = "r",
        track_color: str = "lightgrey",
        handle_style: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def set_val(self, val) -> None: ...
    def on_changed(self, func): ...

class RangeSlider(SliderBase):
    val: Incomplete
    valinit: Incomplete
    track: Incomplete
    poly: Incomplete
    label: Incomplete
    valtext: Incomplete
    def __init__(
        self,
        ax,
        label,
        valmin,
        valmax,
        *,
        valinit: Incomplete | None = None,
        valfmt: Incomplete | None = None,
        closedmin: bool = True,
        closedmax: bool = True,
        dragging: bool = True,
        valstep: Incomplete | None = None,
        orientation: str = "horizontal",
        track_color: str = "lightgrey",
        handle_style: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def set_min(self, min) -> None: ...
    def set_max(self, max) -> None: ...
    def set_val(self, val) -> None: ...
    def on_changed(self, func): ...

class CheckButtons(AxesWidget):
    labels: Incomplete
    def __init__(
        self,
        ax,
        labels,
        actives: Incomplete | None = None,
        *,
        useblit: bool = True,
        label_props: Incomplete | None = None,
        frame_props: Incomplete | None = None,
        check_props: Incomplete | None = None,
    ) -> None: ...
    def set_label_props(self, props) -> None: ...
    def set_frame_props(self, props) -> None: ...
    def set_check_props(self, props) -> None: ...
    def set_active(self, index, state: Incomplete | None = None) -> None: ...
    def clear(self) -> None: ...
    def get_status(self): ...
    def get_checked_labels(self): ...
    def on_clicked(self, func): ...
    def disconnect(self, cid) -> None: ...

class TextBox(AxesWidget):
    label: Incomplete
    text_disp: Incomplete
    cursor_index: int
    cursor: Incomplete
    color: Incomplete
    hovercolor: Incomplete
    capturekeystrokes: bool
    def __init__(
        self,
        ax,
        label,
        initial: str = "",
        *,
        color: str = ".95",
        hovercolor: str = "1",
        label_pad: float = 0.01,
        textalignment: str = "left",
    ) -> None: ...
    @property
    def text(self): ...
    def set_val(self, val) -> None: ...
    def begin_typing(self) -> None: ...
    def stop_typing(self) -> None: ...
    def on_text_change(self, func): ...
    def on_submit(self, func): ...
    def disconnect(self, cid) -> None: ...

class RadioButtons(AxesWidget):
    value_selected: Incomplete
    index_selected: Incomplete
    labels: Incomplete
    def __init__(
        self,
        ax,
        labels,
        active: int = 0,
        activecolor: Incomplete | None = None,
        *,
        useblit: bool = True,
        label_props: Incomplete | None = None,
        radio_props: Incomplete | None = None,
    ) -> None: ...
    def set_label_props(self, props) -> None: ...
    def set_radio_props(self, props) -> None: ...
    @property
    def activecolor(self): ...
    @activecolor.setter
    def activecolor(self, activecolor) -> None: ...
    def set_active(self, index) -> None: ...
    def clear(self) -> None: ...
    def on_clicked(self, func): ...
    def disconnect(self, cid) -> None: ...

class SubplotTool(Widget):
    figure: Incomplete
    targetfig: Incomplete
    buttonreset: Incomplete
    def __init__(self, targetfig, toolfig) -> None: ...

class Cursor(AxesWidget):
    visible: bool
    horizOn: Incomplete
    vertOn: Incomplete
    useblit: Incomplete
    lineh: Incomplete
    linev: Incomplete
    background: Incomplete
    needclear: bool
    def __init__(
        self,
        ax,
        *,
        horizOn: bool = True,
        vertOn: bool = True,
        useblit: bool = False,
        **lineprops,
    ) -> None: ...
    def clear(self, event) -> None: ...
    def onmove(self, event) -> None: ...

class MultiCursor(Widget):
    axes: Incomplete
    horizOn: Incomplete
    vertOn: Incomplete
    visible: bool
    useblit: Incomplete
    vlines: Incomplete
    hlines: Incomplete
    def __init__(
        self,
        canvas,
        axes,
        *,
        useblit: bool = True,
        horizOn: bool = False,
        vertOn: bool = True,
        **lineprops,
    ) -> None: ...
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def clear(self, event) -> None: ...
    def onmove(self, event) -> None: ...

class _SelectorWidget(AxesWidget):
    onselect: Incomplete
    useblit: Incomplete
    background: Incomplete
    validButtons: Incomplete
    def __init__(
        self,
        ax,
        onselect,
        useblit: bool = False,
        button: Incomplete | None = None,
        state_modifier_keys: Incomplete | None = None,
        use_data_coordinates: bool = False,
    ) -> None: ...
    def set_active(self, active) -> None: ...
    def update_background(self, event): ...
    def connect_default_events(self) -> None: ...
    def ignore(self, event): ...
    def update(self): ...
    def press(self, event): ...
    def release(self, event): ...
    def onmove(self, event): ...
    def on_scroll(self, event) -> None: ...
    def on_key_press(self, event) -> None: ...
    def on_key_release(self, event) -> None: ...
    def set_visible(self, visible) -> None: ...
    def get_visible(self): ...
    @property
    def visible(self): ...
    def clear(self) -> None: ...
    @property
    def artists(self): ...
    def set_props(self, **props) -> None: ...
    def set_handle_props(self, **handle_props) -> None: ...
    def add_state(self, state) -> None: ...
    def remove_state(self, state) -> None: ...

class SpanSelector(_SelectorWidget):
    snap_values: Incomplete
    onmove_callback: Incomplete
    minspan: Incomplete
    grab_range: Incomplete
    drag_from_anywhere: Incomplete
    ignore_event_outside: Incomplete
    canvas: Incomplete
    def __init__(
        self,
        ax,
        onselect,
        direction,
        *,
        minspan: int = 0,
        useblit: bool = False,
        props: Incomplete | None = None,
        onmove_callback: Incomplete | None = None,
        interactive: bool = False,
        button: Incomplete | None = None,
        handle_props: Incomplete | None = None,
        grab_range: int = 10,
        state_modifier_keys: Incomplete | None = None,
        drag_from_anywhere: bool = False,
        ignore_event_outside: bool = False,
        snap_values: Incomplete | None = None,
    ) -> None: ...
    ax: Incomplete
    def new_axes(self, ax, *, _props: Incomplete | None = None) -> None: ...
    def connect_default_events(self) -> None: ...
    @property
    def direction(self): ...
    @direction.setter
    def direction(self, direction) -> None: ...
    @property
    def extents(self): ...
    @extents.setter
    def extents(self, extents) -> None: ...

class ToolLineHandles:
    ax: Incomplete
    def __init__(
        self,
        ax,
        positions,
        direction,
        *,
        line_props: Incomplete | None = None,
        useblit: bool = True,
    ) -> None: ...
    @property
    def artists(self): ...
    @property
    def positions(self): ...
    @property
    def direction(self): ...
    def set_data(self, positions) -> None: ...
    def set_visible(self, value) -> None: ...
    def set_animated(self, value) -> None: ...
    def remove(self) -> None: ...
    def closest(self, x, y): ...

class ToolHandles:
    ax: Incomplete
    def __init__(
        self,
        ax,
        x,
        y,
        *,
        marker: str = "o",
        marker_props: Incomplete | None = None,
        useblit: bool = True,
    ) -> None: ...
    @property
    def x(self): ...
    @property
    def y(self): ...
    @property
    def artists(self): ...
    def set_data(self, pts, y: Incomplete | None = None) -> None: ...
    def set_visible(self, val) -> None: ...
    def set_animated(self, val) -> None: ...
    def closest(self, x, y): ...

class RectangleSelector(_SelectorWidget):
    drag_from_anywhere: Incomplete
    ignore_event_outside: Incomplete
    minspanx: Incomplete
    minspany: Incomplete
    spancoords: Incomplete
    grab_range: Incomplete
    def __init__(
        self,
        ax,
        onselect,
        *,
        minspanx: int = 0,
        minspany: int = 0,
        useblit: bool = False,
        props: Incomplete | None = None,
        spancoords: str = "data",
        button: Incomplete | None = None,
        grab_range: int = 10,
        handle_props: Incomplete | None = None,
        interactive: bool = False,
        state_modifier_keys: Incomplete | None = None,
        drag_from_anywhere: bool = False,
        ignore_event_outside: bool = False,
        use_data_coordinates: bool = False,
    ) -> None: ...
    @property
    def corners(self): ...
    @property
    def edge_centers(self): ...
    @property
    def center(self): ...
    @property
    def extents(self): ...
    @extents.setter
    def extents(self, extents) -> None: ...
    @property
    def rotation(self): ...
    @rotation.setter
    def rotation(self, value) -> None: ...
    @property
    def geometry(self): ...

class EllipseSelector(RectangleSelector): ...

class LassoSelector(_SelectorWidget):
    verts: Incomplete
    def __init__(
        self,
        ax,
        onselect,
        *,
        useblit: bool = True,
        props: Incomplete | None = None,
        button: Incomplete | None = None,
    ) -> None: ...

class PolygonSelector(_SelectorWidget):
    grab_range: Incomplete
    def __init__(
        self,
        ax,
        onselect,
        *,
        useblit: bool = False,
        props: Incomplete | None = None,
        handle_props: Incomplete | None = None,
        grab_range: int = 10,
        draw_bounding_box: bool = False,
        box_handle_props: Incomplete | None = None,
        box_props: Incomplete | None = None,
    ) -> None: ...
    def onmove(self, event): ...
    @property
    def verts(self): ...
    @verts.setter
    def verts(self, xys) -> None: ...

class Lasso(AxesWidget):
    useblit: Incomplete
    background: Incomplete
    verts: Incomplete
    line: Incomplete
    callback: Incomplete
    def __init__(
        self, ax, xy, callback, *, useblit: bool = True, props: Incomplete | None = None
    ) -> None: ...
    def onrelease(self, event) -> None: ...
    def onmove(self, event) -> None: ...

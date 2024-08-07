from collections.abc import Generator, Sequence

import matplotlib.artist as martist
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import offsetbox as offsetbox
from matplotlib.cbook import index_of as index_of
from matplotlib.gridspec import SubplotSpec as SubplotSpec
from matplotlib.rcsetup import cycler as cycler
from matplotlib.rcsetup import validate_axisbelow as validate_axisbelow

class _axis_method_wrapper:
    attr_name: Incomplete
    method_name: Incomplete
    __doc__: Incomplete
    def __init__(
        self, attr_name, method_name, *, doc_sub: Incomplete | None = None
    ) -> None: ...
    def __set_name__(self, owner, name): ...

class _TransformedBoundsLocator:
    def __init__(self, bounds, transform) -> None: ...
    def __call__(self, ax, renderer): ...

class _process_plot_var_args:
    command: Incomplete
    def __init__(self, command: str = "plot") -> None: ...
    def set_prop_cycle(self, cycler) -> None: ...
    def __call__(
        self, axes, *args, data: Incomplete | None = None, **kwargs
    ) -> Generator[Incomplete, Incomplete, None]: ...
    def get_next_color(self): ...

class _AxesBase(martist.Artist):
    name: str
    axes: Incomplete
    spines: Incomplete
    fmt_xdata: Incomplete
    fmt_ydata: Incomplete
    def __init__(
        self,
        fig,
        *args,
        facecolor: Incomplete | None = None,
        frameon: bool = True,
        sharex: Incomplete | None = None,
        sharey: Incomplete | None = None,
        label: str = "",
        xscale: Incomplete | None = None,
        yscale: Incomplete | None = None,
        box_aspect: Incomplete | None = None,
        forward_navigation_events: str = "auto",
        **kwargs,
    ) -> None: ...
    def __init_subclass__(cls, **kwargs) -> None: ...
    def get_subplotspec(self): ...
    def set_subplotspec(self, subplotspec) -> None: ...
    def get_gridspec(self): ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    bbox: Incomplete
    dataLim: Incomplete
    transScale: Incomplete
    def set_figure(self, fig) -> None: ...
    @property
    def viewLim(self): ...
    def get_xaxis_transform(self, which: str = "grid"): ...
    def get_xaxis_text1_transform(self, pad_points): ...
    def get_xaxis_text2_transform(self, pad_points): ...
    def get_yaxis_transform(self, which: str = "grid"): ...
    def get_yaxis_text1_transform(self, pad_points): ...
    def get_yaxis_text2_transform(self, pad_points): ...
    def get_position(self, original: bool = False): ...
    def set_position(self, pos, which: str = "both") -> None: ...
    def reset_position(self) -> None: ...
    stale: bool
    def set_axes_locator(self, locator) -> None: ...
    def get_axes_locator(self): ...
    def sharex(self, other) -> None: ...
    def sharey(self, other) -> None: ...
    def clear(self) -> None: ...
    def cla(self) -> None: ...

    class ArtistList(Sequence):
        def __init__(
            self,
            axes,
            prop_name,
            valid_types: Incomplete | None = None,
            invalid_types: Incomplete | None = None,
        ) -> None: ...
        def __len__(self) -> int: ...
        def __iter__(self): ...
        def __getitem__(self, key): ...
        def __add__(self, other): ...
        def __radd__(self, other): ...

    @property
    def artists(self): ...
    @property
    def collections(self): ...
    @property
    def images(self): ...
    @property
    def lines(self): ...
    @property
    def patches(self): ...
    @property
    def tables(self): ...
    @property
    def texts(self): ...
    def get_facecolor(self): ...
    def set_facecolor(self, color): ...
    def set_prop_cycle(self, *args, **kwargs) -> None: ...
    def get_aspect(self): ...
    def set_aspect(
        self,
        aspect,
        adjustable: Incomplete | None = None,
        anchor: Incomplete | None = None,
        share: bool = False,
    ) -> None: ...
    def get_adjustable(self): ...
    def set_adjustable(self, adjustable, share: bool = False) -> None: ...
    def get_box_aspect(self): ...
    def set_box_aspect(self, aspect: Incomplete | None = None) -> None: ...
    def get_anchor(self): ...
    def set_anchor(self, anchor, share: bool = False) -> None: ...
    def get_data_ratio(self): ...
    def apply_aspect(self, position: Incomplete | None = None) -> None: ...
    def axis(
        self, arg: Incomplete | None = None, /, *, emit: bool = True, **kwargs
    ): ...
    def get_legend(self): ...
    def get_images(self): ...
    def get_lines(self): ...
    def get_xaxis(self): ...
    def get_yaxis(self): ...
    get_xgridlines: Incomplete
    get_xticklines: Incomplete
    get_ygridlines: Incomplete
    get_yticklines: Incomplete
    def has_data(self): ...
    def add_artist(self, a): ...
    def add_child_axes(self, ax): ...
    def add_collection(self, collection, autolim: bool = True): ...
    def add_image(self, image): ...
    def add_line(self, line): ...
    def add_patch(self, p): ...
    def add_table(self, tab): ...
    def add_container(self, container): ...
    ignore_existing_data_limits: bool
    def relim(self, visible_only: bool = False) -> None: ...
    def update_datalim(
        self, xys, updatex: bool = True, updatey: bool = True
    ) -> None: ...
    def in_axes(self, mouseevent): ...
    get_autoscalex_on: Incomplete
    get_autoscaley_on: Incomplete
    set_autoscalex_on: Incomplete
    set_autoscaley_on: Incomplete
    def get_autoscale_on(self): ...
    def set_autoscale_on(self, b) -> None: ...
    @property
    def use_sticky_edges(self): ...
    @use_sticky_edges.setter
    def use_sticky_edges(self, b) -> None: ...
    def get_xmargin(self): ...
    def get_ymargin(self): ...
    def set_xmargin(self, m) -> None: ...
    def set_ymargin(self, m) -> None: ...
    def margins(
        self,
        *margins,
        x: Incomplete | None = None,
        y: Incomplete | None = None,
        tight: bool = True,
    ): ...
    def set_rasterization_zorder(self, z) -> None: ...
    def get_rasterization_zorder(self): ...
    def autoscale(
        self, enable: bool = True, axis: str = "both", tight: Incomplete | None = None
    ) -> None: ...
    def autoscale_view(
        self, tight: Incomplete | None = None, scalex: bool = True, scaley: bool = True
    ) -> None: ...
    def draw(self, renderer) -> None: ...
    def draw_artist(self, a) -> None: ...
    def redraw_in_frame(self) -> None: ...
    def get_frame_on(self): ...
    def set_frame_on(self, b) -> None: ...
    def get_axisbelow(self): ...
    def set_axisbelow(self, b) -> None: ...
    def grid(
        self,
        visible: Incomplete | None = None,
        which: str = "major",
        axis: str = "both",
        **kwargs,
    ) -> None: ...
    def ticklabel_format(
        self,
        *,
        axis: str = "both",
        style: Incomplete | None = None,
        scilimits: Incomplete | None = None,
        useOffset: Incomplete | None = None,
        useLocale: Incomplete | None = None,
        useMathText: Incomplete | None = None,
    ) -> None: ...
    def locator_params(
        self, axis: str = "both", tight: Incomplete | None = None, **kwargs
    ) -> None: ...
    def tick_params(self, axis: str = "both", **kwargs) -> None: ...
    axison: bool
    def set_axis_off(self) -> None: ...
    def set_axis_on(self) -> None: ...
    def get_xlabel(self): ...
    def set_xlabel(
        self,
        xlabel,
        fontdict: Incomplete | None = None,
        labelpad: Incomplete | None = None,
        *,
        loc: Incomplete | None = None,
        **kwargs,
    ): ...
    def invert_xaxis(self) -> None: ...
    xaxis_inverted: Incomplete
    def get_xbound(self): ...
    def set_xbound(
        self, lower: Incomplete | None = None, upper: Incomplete | None = None
    ) -> None: ...
    def get_xlim(self): ...
    def set_xlim(
        self,
        left: Incomplete | None = None,
        right: Incomplete | None = None,
        *,
        emit: bool = True,
        auto: bool = False,
        xmin: Incomplete | None = None,
        xmax: Incomplete | None = None,
    ): ...
    get_xscale: Incomplete
    set_xscale: Incomplete
    get_xticks: Incomplete
    set_xticks: Incomplete
    get_xmajorticklabels: Incomplete
    get_xminorticklabels: Incomplete
    get_xticklabels: Incomplete
    set_xticklabels: Incomplete
    def get_ylabel(self): ...
    def set_ylabel(
        self,
        ylabel,
        fontdict: Incomplete | None = None,
        labelpad: Incomplete | None = None,
        *,
        loc: Incomplete | None = None,
        **kwargs,
    ): ...
    def invert_yaxis(self) -> None: ...
    yaxis_inverted: Incomplete
    def get_ybound(self): ...
    def set_ybound(
        self, lower: Incomplete | None = None, upper: Incomplete | None = None
    ) -> None: ...
    def get_ylim(self): ...
    def set_ylim(
        self,
        bottom: Incomplete | None = None,
        top: Incomplete | None = None,
        *,
        emit: bool = True,
        auto: bool = False,
        ymin: Incomplete | None = None,
        ymax: Incomplete | None = None,
    ): ...
    get_yscale: Incomplete
    set_yscale: Incomplete
    get_yticks: Incomplete
    set_yticks: Incomplete
    get_ymajorticklabels: Incomplete
    get_yminorticklabels: Incomplete
    get_yticklabels: Incomplete
    set_yticklabels: Incomplete
    xaxis_date: Incomplete
    yaxis_date: Incomplete
    def format_xdata(self, x): ...
    def format_ydata(self, y): ...
    def format_coord(self, x, y): ...
    def minorticks_on(self) -> None: ...
    def minorticks_off(self) -> None: ...
    def can_zoom(self): ...
    def can_pan(self): ...
    def get_navigate(self): ...
    def set_navigate(self, b) -> None: ...
    def get_navigate_mode(self): ...
    def set_navigate_mode(self, b) -> None: ...
    def start_pan(self, x, y, button) -> None: ...
    def end_pan(self) -> None: ...
    def drag_pan(self, button, key, x, y) -> None: ...
    def get_children(self): ...
    def contains(self, mouseevent): ...
    def contains_point(self, point): ...
    def get_default_bbox_extra_artists(self): ...
    def get_tightbbox(
        self,
        renderer: Incomplete | None = None,
        call_axes_locator: bool = True,
        bbox_extra_artists: Incomplete | None = None,
        *,
        for_layout_only: bool = False,
    ): ...
    def twinx(self): ...
    def twiny(self): ...
    def get_shared_x_axes(self): ...
    def get_shared_y_axes(self): ...
    def label_outer(self, remove_inner_ticks: bool = False) -> None: ...
    def set_forward_navigation_events(self, forward) -> None: ...
    def get_forward_navigation_events(self): ...

from _typeshed import Incomplete
from matplotlib.axes._base import _AxesBase
from matplotlib.axes._secondary_axes import SecondaryAxis as SecondaryAxis
from matplotlib.container import BarContainer as BarContainer
from matplotlib.container import ErrorbarContainer as ErrorbarContainer
from matplotlib.container import StemContainer as StemContainer

class Axes(_AxesBase):
    def get_title(self, loc: str = "center"): ...
    def set_title(
        self,
        label,
        fontdict: Incomplete | None = None,
        loc: Incomplete | None = None,
        pad: Incomplete | None = None,
        *,
        y: Incomplete | None = None,
        **kwargs,
    ): ...
    def get_legend_handles_labels(
        self, legend_handler_map: Incomplete | None = None
    ): ...
    legend_: Incomplete
    def legend(self, *args, **kwargs): ...
    def inset_axes(
        self, bounds, *, transform: Incomplete | None = None, zorder: int = 5, **kwargs
    ): ...
    def indicate_inset(
        self,
        bounds,
        inset_ax: Incomplete | None = None,
        *,
        transform: Incomplete | None = None,
        facecolor: str = "none",
        edgecolor: str = "0.5",
        alpha: float = 0.5,
        zorder: float = 4.99,
        **kwargs,
    ): ...
    def indicate_inset_zoom(self, inset_ax, **kwargs): ...
    def secondary_xaxis(
        self,
        location,
        *,
        functions: Incomplete | None = None,
        transform: Incomplete | None = None,
        **kwargs,
    ): ...
    def secondary_yaxis(
        self,
        location,
        *,
        functions: Incomplete | None = None,
        transform: Incomplete | None = None,
        **kwargs,
    ): ...
    def text(self, x, y, s, fontdict: Incomplete | None = None, **kwargs): ...
    def annotate(
        self,
        text,
        xy,
        xytext: Incomplete | None = None,
        xycoords: str = "data",
        textcoords: Incomplete | None = None,
        arrowprops: Incomplete | None = None,
        annotation_clip: Incomplete | None = None,
        **kwargs,
    ): ...
    def axhline(self, y: int = 0, xmin: int = 0, xmax: int = 1, **kwargs): ...
    def axvline(self, x: int = 0, ymin: int = 0, ymax: int = 1, **kwargs): ...
    def axline(
        self,
        xy1,
        xy2: Incomplete | None = None,
        *,
        slope: Incomplete | None = None,
        **kwargs,
    ): ...
    def axhspan(self, ymin, ymax, xmin: int = 0, xmax: int = 1, **kwargs): ...
    def axvspan(self, xmin, xmax, ymin: int = 0, ymax: int = 1, **kwargs): ...
    def hlines(
        self,
        y,
        xmin,
        xmax,
        colors: Incomplete | None = None,
        linestyles: str = "solid",
        label: str = "",
        **kwargs,
    ): ...
    def vlines(
        self,
        x,
        ymin,
        ymax,
        colors: Incomplete | None = None,
        linestyles: str = "solid",
        label: str = "",
        **kwargs,
    ): ...
    def eventplot(
        self,
        positions,
        orientation: str = "horizontal",
        lineoffsets: int = 1,
        linelengths: int = 1,
        linewidths: Incomplete | None = None,
        colors: Incomplete | None = None,
        alpha: Incomplete | None = None,
        linestyles: str = "solid",
        **kwargs,
    ): ...
    def plot(
        self,
        *args,
        scalex: bool = True,
        scaley: bool = True,
        data: Incomplete | None = None,
        **kwargs,
    ): ...
    def plot_date(
        self,
        x,
        y,
        fmt: str = "o",
        tz: Incomplete | None = None,
        xdate: bool = True,
        ydate: bool = False,
        **kwargs,
    ): ...
    def loglog(self, *args, **kwargs): ...
    def semilogx(self, *args, **kwargs): ...
    def semilogy(self, *args, **kwargs): ...
    def acorr(self, x, **kwargs): ...
    def xcorr(
        self,
        x,
        y,
        normed: bool = True,
        detrend=...,
        usevlines: bool = True,
        maxlags: int = 10,
        **kwargs,
    ): ...
    def step(
        self, x, y, *args, where: str = "pre", data: Incomplete | None = None, **kwargs
    ): ...
    def bar(
        self,
        x,
        height,
        width: float = 0.8,
        bottom: Incomplete | None = None,
        *,
        align: str = "center",
        **kwargs,
    ): ...
    def barh(
        self,
        y,
        width,
        height: float = 0.8,
        left: Incomplete | None = None,
        *,
        align: str = "center",
        data: Incomplete | None = None,
        **kwargs,
    ): ...
    def bar_label(
        self,
        container,
        labels: Incomplete | None = None,
        *,
        fmt: str = "%g",
        label_type: str = "edge",
        padding: int = 0,
        **kwargs,
    ): ...
    def broken_barh(self, xranges, yrange, **kwargs): ...
    def stem(
        self,
        *args,
        linefmt: Incomplete | None = None,
        markerfmt: Incomplete | None = None,
        basefmt: Incomplete | None = None,
        bottom: int = 0,
        label: Incomplete | None = None,
        orientation: str = "vertical",
    ): ...
    def pie(
        self,
        x,
        explode: Incomplete | None = None,
        labels: Incomplete | None = None,
        colors: Incomplete | None = None,
        autopct: Incomplete | None = None,
        pctdistance: float = 0.6,
        shadow: bool = False,
        labeldistance: float = 1.1,
        startangle: int = 0,
        radius: int = 1,
        counterclock: bool = True,
        wedgeprops: Incomplete | None = None,
        textprops: Incomplete | None = None,
        center=(0, 0),
        frame: bool = False,
        rotatelabels: bool = False,
        *,
        normalize: bool = True,
        hatch: Incomplete | None = None,
    ): ...
    def errorbar(
        self,
        x,
        y,
        yerr: Incomplete | None = None,
        xerr: Incomplete | None = None,
        fmt: str = "",
        ecolor: Incomplete | None = None,
        elinewidth: Incomplete | None = None,
        capsize: Incomplete | None = None,
        barsabove: bool = False,
        lolims: bool = False,
        uplims: bool = False,
        xlolims: bool = False,
        xuplims: bool = False,
        errorevery: int = 1,
        capthick: Incomplete | None = None,
        **kwargs,
    ): ...
    def boxplot(
        self,
        x,
        notch: Incomplete | None = None,
        sym: Incomplete | None = None,
        vert: Incomplete | None = None,
        whis: Incomplete | None = None,
        positions: Incomplete | None = None,
        widths: Incomplete | None = None,
        patch_artist: Incomplete | None = None,
        bootstrap: Incomplete | None = None,
        usermedians: Incomplete | None = None,
        conf_intervals: Incomplete | None = None,
        meanline: Incomplete | None = None,
        showmeans: Incomplete | None = None,
        showcaps: Incomplete | None = None,
        showbox: Incomplete | None = None,
        showfliers: Incomplete | None = None,
        boxprops: Incomplete | None = None,
        tick_labels: Incomplete | None = None,
        flierprops: Incomplete | None = None,
        medianprops: Incomplete | None = None,
        meanprops: Incomplete | None = None,
        capprops: Incomplete | None = None,
        whiskerprops: Incomplete | None = None,
        manage_ticks: bool = True,
        autorange: bool = False,
        zorder: Incomplete | None = None,
        capwidths: Incomplete | None = None,
        label: Incomplete | None = None,
    ): ...
    def bxp(
        self,
        bxpstats,
        positions: Incomplete | None = None,
        widths: Incomplete | None = None,
        vert: bool = True,
        patch_artist: bool = False,
        shownotches: bool = False,
        showmeans: bool = False,
        showcaps: bool = True,
        showbox: bool = True,
        showfliers: bool = True,
        boxprops: Incomplete | None = None,
        whiskerprops: Incomplete | None = None,
        flierprops: Incomplete | None = None,
        medianprops: Incomplete | None = None,
        capprops: Incomplete | None = None,
        meanprops: Incomplete | None = None,
        meanline: bool = False,
        manage_ticks: bool = True,
        zorder: Incomplete | None = None,
        capwidths: Incomplete | None = None,
        label: Incomplete | None = None,
    ): ...
    def scatter(
        self,
        x,
        y,
        s: Incomplete | None = None,
        c: Incomplete | None = None,
        marker: Incomplete | None = None,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        alpha: Incomplete | None = None,
        linewidths: Incomplete | None = None,
        *,
        edgecolors: Incomplete | None = None,
        plotnonfinite: bool = False,
        **kwargs,
    ): ...
    def hexbin(
        self,
        x,
        y,
        C: Incomplete | None = None,
        gridsize: int = 100,
        bins: Incomplete | None = None,
        xscale: str = "linear",
        yscale: str = "linear",
        extent: Incomplete | None = None,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        alpha: Incomplete | None = None,
        linewidths: Incomplete | None = None,
        edgecolors: str = "face",
        reduce_C_function=...,
        mincnt: Incomplete | None = None,
        marginals: bool = False,
        **kwargs,
    ): ...
    def arrow(self, x, y, dx, dy, **kwargs): ...
    def quiverkey(self, Q, X, Y, U, label, **kwargs): ...
    def quiver(self, *args, **kwargs): ...
    def barbs(self, *args, **kwargs): ...
    def fill(self, *args, data: Incomplete | None = None, **kwargs): ...
    def fill_between(
        self,
        x,
        y1,
        y2: int = 0,
        where: Incomplete | None = None,
        interpolate: bool = False,
        step: Incomplete | None = None,
        **kwargs,
    ): ...
    fill_between: Incomplete
    def fill_betweenx(
        self,
        y,
        x1,
        x2: int = 0,
        where: Incomplete | None = None,
        step: Incomplete | None = None,
        interpolate: bool = False,
        **kwargs,
    ): ...
    fill_betweenx: Incomplete
    def imshow(
        self,
        X,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        *,
        aspect: Incomplete | None = None,
        interpolation: Incomplete | None = None,
        alpha: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        origin: Incomplete | None = None,
        extent: Incomplete | None = None,
        interpolation_stage: Incomplete | None = None,
        filternorm: bool = True,
        filterrad: float = 4.0,
        resample: Incomplete | None = None,
        url: Incomplete | None = None,
        **kwargs,
    ): ...
    def pcolor(
        self,
        *args,
        shading: Incomplete | None = None,
        alpha: Incomplete | None = None,
        norm: Incomplete | None = None,
        cmap: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        **kwargs,
    ): ...
    def pcolormesh(
        self,
        *args,
        alpha: Incomplete | None = None,
        norm: Incomplete | None = None,
        cmap: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        shading: Incomplete | None = None,
        antialiased: bool = False,
        **kwargs,
    ): ...
    def pcolorfast(
        self,
        *args,
        alpha: Incomplete | None = None,
        norm: Incomplete | None = None,
        cmap: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        **kwargs,
    ): ...
    def contour(self, *args, **kwargs): ...
    def contourf(self, *args, **kwargs): ...
    def clabel(self, CS, levels: Incomplete | None = None, **kwargs): ...
    def hist(
        self,
        x,
        bins: Incomplete | None = None,
        range: Incomplete | None = None,
        density: bool = False,
        weights: Incomplete | None = None,
        cumulative: bool = False,
        bottom: Incomplete | None = None,
        histtype: str = "bar",
        align: str = "mid",
        orientation: str = "vertical",
        rwidth: Incomplete | None = None,
        log: bool = False,
        color: Incomplete | None = None,
        label: Incomplete | None = None,
        stacked: bool = False,
        **kwargs,
    ): ...
    def stairs(
        self,
        values,
        edges: Incomplete | None = None,
        *,
        orientation: str = "vertical",
        baseline: int = 0,
        fill: bool = False,
        **kwargs,
    ): ...
    def hist2d(
        self,
        x,
        y,
        bins: int = 10,
        range: Incomplete | None = None,
        density: bool = False,
        weights: Incomplete | None = None,
        cmin: Incomplete | None = None,
        cmax: Incomplete | None = None,
        **kwargs,
    ): ...
    def ecdf(
        self,
        x,
        weights: Incomplete | None = None,
        *,
        complementary: bool = False,
        orientation: str = "vertical",
        compress: bool = False,
        **kwargs,
    ): ...
    def psd(
        self,
        x,
        NFFT: Incomplete | None = None,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        detrend: Incomplete | None = None,
        window: Incomplete | None = None,
        noverlap: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        scale_by_freq: Incomplete | None = None,
        return_line: Incomplete | None = None,
        **kwargs,
    ): ...
    def csd(
        self,
        x,
        y,
        NFFT: Incomplete | None = None,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        detrend: Incomplete | None = None,
        window: Incomplete | None = None,
        noverlap: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        scale_by_freq: Incomplete | None = None,
        return_line: Incomplete | None = None,
        **kwargs,
    ): ...
    def magnitude_spectrum(
        self,
        x,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        window: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        scale: Incomplete | None = None,
        **kwargs,
    ): ...
    def angle_spectrum(
        self,
        x,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        window: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        **kwargs,
    ): ...
    def phase_spectrum(
        self,
        x,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        window: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        **kwargs,
    ): ...
    def cohere(
        self,
        x,
        y,
        NFFT: int = 256,
        Fs: int = 2,
        Fc: int = 0,
        detrend=...,
        window=...,
        noverlap: int = 0,
        pad_to: Incomplete | None = None,
        sides: str = "default",
        scale_by_freq: Incomplete | None = None,
        **kwargs,
    ): ...
    def specgram(
        self,
        x,
        NFFT: Incomplete | None = None,
        Fs: Incomplete | None = None,
        Fc: Incomplete | None = None,
        detrend: Incomplete | None = None,
        window: Incomplete | None = None,
        noverlap: Incomplete | None = None,
        cmap: Incomplete | None = None,
        xextent: Incomplete | None = None,
        pad_to: Incomplete | None = None,
        sides: Incomplete | None = None,
        scale_by_freq: Incomplete | None = None,
        mode: Incomplete | None = None,
        scale: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        **kwargs,
    ): ...
    def spy(
        self,
        Z,
        precision: int = 0,
        marker: Incomplete | None = None,
        markersize: Incomplete | None = None,
        aspect: str = "equal",
        origin: str = "upper",
        **kwargs,
    ): ...
    def matshow(self, Z, **kwargs): ...
    def violinplot(
        self,
        dataset,
        positions: Incomplete | None = None,
        vert: bool = True,
        widths: float = 0.5,
        showmeans: bool = False,
        showextrema: bool = True,
        showmedians: bool = False,
        quantiles: Incomplete | None = None,
        points: int = 100,
        bw_method: Incomplete | None = None,
        side: str = "both",
    ): ...
    def violin(
        self,
        vpstats,
        positions: Incomplete | None = None,
        vert: bool = True,
        widths: float = 0.5,
        showmeans: bool = False,
        showextrema: bool = True,
        showmedians: bool = False,
        side: str = "both",
    ): ...
    table: Incomplete
    stackplot: Incomplete
    streamplot: Incomplete
    tricontour: Incomplete
    tricontourf: Incomplete
    tripcolor: Incomplete
    triplot: Incomplete

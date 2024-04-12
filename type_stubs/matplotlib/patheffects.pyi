from _typeshed import Incomplete
from matplotlib.backend_bases import RendererBase as RendererBase
from matplotlib.path import Path as Path

class AbstractPathEffect:
    def __init__(self, offset=(0.0, 0.0)) -> None: ...
    def draw_path(
        self, renderer, gc, tpath, affine, rgbFace: Incomplete | None = None
    ): ...

class PathEffectRenderer(RendererBase):
    def __init__(self, path_effects, renderer) -> None: ...
    def copy_with_path_effect(self, path_effects): ...
    def draw_path(
        self, gc, tpath, affine, rgbFace: Incomplete | None = None
    ) -> None: ...
    def draw_markers(self, gc, marker_path, marker_trans, path, *args, **kwargs): ...
    def draw_path_collection(self, gc, master_transform, paths, *args, **kwargs): ...
    def __getattribute__(self, name): ...

class Normal(AbstractPathEffect): ...

class Stroke(AbstractPathEffect):
    def __init__(self, offset=(0, 0), **kwargs) -> None: ...
    def draw_path(self, renderer, gc, tpath, affine, rgbFace) -> None: ...

withStroke: Incomplete

class SimplePatchShadow(AbstractPathEffect):
    def __init__(
        self,
        offset=(2, -2),
        shadow_rgbFace: Incomplete | None = None,
        alpha: Incomplete | None = None,
        rho: float = 0.3,
        **kwargs,
    ) -> None: ...
    def draw_path(self, renderer, gc, tpath, affine, rgbFace) -> None: ...

withSimplePatchShadow: Incomplete

class SimpleLineShadow(AbstractPathEffect):
    def __init__(
        self,
        offset=(2, -2),
        shadow_color: str = "k",
        alpha: float = 0.3,
        rho: float = 0.3,
        **kwargs,
    ) -> None: ...
    def draw_path(self, renderer, gc, tpath, affine, rgbFace) -> None: ...

class PathPatchEffect(AbstractPathEffect):
    patch: Incomplete
    def __init__(self, offset=(0, 0), **kwargs) -> None: ...
    def draw_path(self, renderer, gc, tpath, affine, rgbFace) -> None: ...

class TickedStroke(AbstractPathEffect):
    def __init__(
        self,
        offset=(0, 0),
        spacing: float = 10.0,
        angle: float = 45.0,
        length=...,
        **kwargs,
    ) -> None: ...
    def draw_path(self, renderer, gc, tpath, affine, rgbFace) -> None: ...

withTickedStroke: Incomplete

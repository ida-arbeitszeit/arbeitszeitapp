import enum
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib._pylab_helpers import Gcf as Gcf

class Cursors(enum.IntEnum):
    POINTER: Incomplete
    HAND: Incomplete
    SELECT_REGION: Incomplete
    MOVE: Incomplete
    WAIT: Incomplete
    RESIZE_HORIZONTAL: Incomplete
    RESIZE_VERTICAL: Incomplete
cursors = Cursors

class ToolBase:
    default_keymap: Incomplete
    description: Incomplete
    image: Incomplete
    def __init__(self, toolmanager, name) -> None: ...
    name: Incomplete
    toolmanager: Incomplete
    canvas: Incomplete
    def set_figure(self, figure) -> None: ...
    figure: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolToggleBase(ToolBase):
    radio_group: Incomplete
    cursor: Incomplete
    default_toggled: bool
    def __init__(self, *args, **kwargs) -> None: ...
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...
    def enable(self, event: Incomplete | None = ...) -> None: ...
    def disable(self, event: Incomplete | None = ...) -> None: ...
    @property
    def toggled(self): ...
    def set_figure(self, figure) -> None: ...

class ToolSetCursor(ToolBase):
    def __init__(self, *args, **kwargs) -> None: ...
    def set_figure(self, figure) -> None: ...

class ToolCursorPosition(ToolBase):
    def __init__(self, *args, **kwargs) -> None: ...
    def set_figure(self, figure) -> None: ...
    def send_message(self, event) -> None: ...

class RubberbandBase(ToolBase):
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...
    def draw_rubberband(self, *data) -> None: ...
    def remove_rubberband(self) -> None: ...

class ToolQuit(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolQuitAll(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolGrid(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolMinorGrid(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolFullScreen(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class AxisScaleBase(ToolToggleBase):
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...
    def enable(self, event: Incomplete | None = ...) -> None: ...
    def disable(self, event: Incomplete | None = ...) -> None: ...

class ToolYScale(AxisScaleBase):
    description: str
    default_keymap: Incomplete
    def set_scale(self, ax, scale) -> None: ...

class ToolXScale(AxisScaleBase):
    description: str
    default_keymap: Incomplete
    def set_scale(self, ax, scale) -> None: ...

class ToolViewsPositions(ToolBase):
    views: Incomplete
    positions: Incomplete
    home_views: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def add_figure(self, figure): ...
    def clear(self, figure) -> None: ...
    def update_view(self) -> None: ...
    def push_current(self, figure: Incomplete | None = ...) -> None: ...
    def update_home_views(self, figure: Incomplete | None = ...) -> None: ...
    def home(self) -> None: ...
    def back(self) -> None: ...
    def forward(self) -> None: ...

class ViewsPositionsBase(ToolBase):
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...

class ToolHome(ViewsPositionsBase):
    description: str
    image: str
    default_keymap: Incomplete

class ToolBack(ViewsPositionsBase):
    description: str
    image: str
    default_keymap: Incomplete

class ToolForward(ViewsPositionsBase):
    description: str
    image: str
    default_keymap: Incomplete

class ConfigureSubplotsBase(ToolBase):
    description: str
    image: str

class SaveFigureBase(ToolBase):
    description: str
    image: str
    default_keymap: Incomplete

class ZoomPanBase(ToolToggleBase):
    base_scale: float
    scrollthresh: float
    lastscroll: Incomplete
    def __init__(self, *args) -> None: ...
    def enable(self, event: Incomplete | None = ...) -> None: ...
    def disable(self, event: Incomplete | None = ...) -> None: ...
    def trigger(self, sender, event, data: Incomplete | None = ...) -> None: ...
    def scroll_zoom(self, event) -> None: ...

class ToolZoom(ZoomPanBase):
    description: str
    image: str
    default_keymap: Incomplete
    cursor: Incomplete
    radio_group: str
    def __init__(self, *args) -> None: ...

class ToolPan(ZoomPanBase):
    default_keymap: Incomplete
    description: str
    image: str
    cursor: Incomplete
    radio_group: str
    def __init__(self, *args) -> None: ...

class ToolHelpBase(ToolBase):
    description: str
    default_keymap: Incomplete
    image: str
    @staticmethod
    def format_shortcut(key_sequence): ...

class ToolCopyToClipboardBase(ToolBase):
    description: str
    default_keymap: Incomplete
    def trigger(self, *args, **kwargs) -> None: ...

default_tools: Incomplete
default_toolbar_tools: Incomplete

def add_tools_to_manager(toolmanager, tools=...) -> None: ...
def add_tools_to_container(container, tools=...) -> None: ...

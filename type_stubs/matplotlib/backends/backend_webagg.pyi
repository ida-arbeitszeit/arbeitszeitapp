import tornado.web
import tornado.websocket
from _typeshed import Incomplete
from matplotlib._pylab_helpers import Gcf as Gcf
from matplotlib.backend_bases import _Backend

from . import backend_webagg_core as core
from .backend_webagg_core import TimerAsyncio as TimerAsyncio
from .backend_webagg_core import TimerTornado as TimerTornado

webagg_server_thread: Incomplete

class FigureManagerWebAgg(core.FigureManagerWebAgg):
    @classmethod
    def pyplot_show(cls, *, block: Incomplete | None = None) -> None: ...

class FigureCanvasWebAgg(core.FigureCanvasWebAggCore):
    manager_class = FigureManagerWebAgg

class WebAggApplication(tornado.web.Application):
    initialized: bool
    started: bool

    class FavIcon(tornado.web.RequestHandler):
        def get(self) -> None: ...

    class SingleFigurePage(tornado.web.RequestHandler):
        url_prefix: Incomplete
        def __init__(
            self, application, request, *, url_prefix: str = "", **kwargs
        ) -> None: ...
        def get(self, fignum) -> None: ...

    class AllFiguresPage(tornado.web.RequestHandler):
        url_prefix: Incomplete
        def __init__(
            self, application, request, *, url_prefix: str = "", **kwargs
        ) -> None: ...
        def get(self) -> None: ...

    class MplJs(tornado.web.RequestHandler):
        def get(self) -> None: ...

    class Download(tornado.web.RequestHandler):
        def get(self, fignum, fmt) -> None: ...

    class WebSocket(tornado.websocket.WebSocketHandler):
        supports_binary: bool
        fignum: Incomplete
        manager: Incomplete
        def open(self, fignum) -> None: ...
        def on_close(self) -> None: ...
        def on_message(self, message) -> None: ...
        def send_json(self, content) -> None: ...
        def send_binary(self, blob) -> None: ...

    def __init__(self, url_prefix: str = "") -> None: ...
    @classmethod
    def initialize(
        cls,
        url_prefix: str = "",
        port: Incomplete | None = None,
        address: Incomplete | None = None,
    ) -> None: ...
    @classmethod
    def start(cls): ...

def ipython_inline_display(figure): ...

class _BackendWebAgg(_Backend):
    FigureCanvas = FigureCanvasWebAgg
    FigureManager = FigureManagerWebAgg

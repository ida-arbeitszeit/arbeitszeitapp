from typing import NamedTuple

from _typeshed import Incomplete
from matplotlib import cbook as cbook

class Page(NamedTuple):
    text: Incomplete
    boxes: Incomplete
    height: Incomplete
    width: Incomplete
    descent: Incomplete

class Box(NamedTuple):
    x: Incomplete
    y: Incomplete
    height: Incomplete
    width: Incomplete

class Text(
    NamedTuple(
        "Text",
        [
            ("x", Incomplete),
            ("y", Incomplete),
            ("font", Incomplete),
            ("glyph", Incomplete),
            ("width", Incomplete),
        ],
    )
):
    @property
    def font_path(self): ...
    @property
    def font_size(self): ...
    @property
    def font_effects(self): ...
    @property
    def glyph_name_or_index(self): ...

class Dvi:
    file: Incomplete
    dpi: Incomplete
    fonts: Incomplete
    state: Incomplete
    def __init__(self, filename, dpi) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        etype: type[BaseException] | None,
        evalue: BaseException | None,
        etrace: types.TracebackType | None,
    ) -> None: ...
    def __iter__(self): ...
    def close(self) -> None: ...

class DviFont:
    texname: Incomplete
    size: Incomplete
    widths: Incomplete
    def __init__(self, scale, tfm, texname, vf) -> None: ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...

class Vf(Dvi):
    def __init__(self, filename) -> None: ...
    def __getitem__(self, code): ...

class Tfm:
    def __init__(self, filename) -> None: ...

class PsFont(NamedTuple):
    texname: Incomplete
    psname: Incomplete
    effects: Incomplete
    encoding: Incomplete
    filename: Incomplete

class PsfontsMap:
    def __new__(cls, filename): ...
    def __getitem__(self, texname): ...

class _LuatexKpsewhich:
    def __new__(cls): ...
    def search(self, filename): ...

def find_tex_file(filename): ...

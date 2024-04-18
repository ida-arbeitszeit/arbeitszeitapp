from collections.abc import Generator, MutableMapping
from typing import NamedTuple

from _typeshed import Incomplete
from matplotlib._api import MatplotlibDeprecationWarning as MatplotlibDeprecationWarning
from matplotlib.cm import _colormaps as colormaps
from matplotlib.colors import _color_sequences as color_sequences

__all__ = [
    "__bibtex__",
    "__version__",
    "__version_info__",
    "set_loglevel",
    "ExecutableNotFoundError",
    "get_configdir",
    "get_cachedir",
    "get_data_path",
    "matplotlib_fname",
    "MatplotlibDeprecationWarning",
    "RcParams",
    "rc_params",
    "rc_params_from_file",
    "rcParamsDefault",
    "rcParams",
    "rcParamsOrig",
    "defaultParams",
    "rc",
    "rcdefaults",
    "rc_file_defaults",
    "rc_file",
    "rc_context",
    "use",
    "get_backend",
    "interactive",
    "is_interactive",
    "colormaps",
    "color_sequences",
]

__bibtex__: str

class _VersionInfo(NamedTuple):
    major: Incomplete
    minor: Incomplete
    micro: Incomplete
    releaselevel: Incomplete
    serial: Incomplete

class __getattr__:
    __version__: Incomplete
    __version_info__: Incomplete

def set_loglevel(level) -> None: ...

class _ExecInfo(NamedTuple):
    executable: Incomplete
    raw_version: Incomplete
    version: Incomplete

class ExecutableNotFoundError(FileNotFoundError): ...

def get_configdir(): ...
def get_cachedir(): ...
def get_data_path(): ...
def matplotlib_fname(): ...

class RcParams(MutableMapping, dict):
    validate: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def __setitem__(self, key, val) -> None: ...
    def __getitem__(self, key): ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def find_all(self, pattern): ...
    def copy(self): ...

def rc_params(fail_on_error: bool = False): ...
def rc_params_from_file(
    fname, fail_on_error: bool = False, use_default_template: bool = True
): ...

rcParamsDefault: Incomplete
rcParams: Incomplete
rcParamsOrig: Incomplete
defaultParams: Incomplete

def rc(group, **kwargs) -> None: ...
def rcdefaults() -> None: ...
def rc_file_defaults() -> None: ...
def rc_file(fname, *, use_default_template: bool = True) -> None: ...
def rc_context(
    rc: Incomplete | None = None, fname: Incomplete | None = None
) -> Generator[None, None, None]: ...
def use(backend, *, force: bool = True) -> None: ...
def get_backend(): ...
def interactive(b) -> None: ...
def is_interactive(): ...

# Names in __all__ with no definition:
#   __version__
#   __version_info__

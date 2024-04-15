from collections.abc import Generator

from _typeshed import Incomplete

class MatplotlibDeprecationWarning(DeprecationWarning): ...

def warn_deprecated(
    since,
    *,
    message: str = "",
    name: str = "",
    alternative: str = "",
    pending: bool = False,
    obj_type: str = "",
    addendum: str = "",
    removal: str = "",
) -> None: ...
def deprecated(
    since,
    *,
    message: str = "",
    name: str = "",
    alternative: str = "",
    pending: bool = False,
    obj_type: Incomplete | None = None,
    addendum: str = "",
    removal: str = "",
): ...

class deprecate_privatize_attribute:
    deprecator: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def __set_name__(self, owner, name): ...

DECORATORS: Incomplete

def rename_parameter(since, old, new, func: Incomplete | None = None): ...

class _deprecated_parameter_class: ...

def delete_parameter(since, name, func: Incomplete | None = None, **kwargs): ...
def make_keyword_only(since, name, func: Incomplete | None = None): ...
def deprecate_method_override(method, obj, *, allow_empty: bool = False, **kwargs): ...
def suppress_matplotlib_deprecation_warning() -> Generator[None, None, None]: ...

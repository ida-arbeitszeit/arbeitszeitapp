from collections.abc import Generator

from _typeshed import Incomplete

__all__ = ["use", "context", "available", "library", "reload_library"]

def use(style) -> None: ...
def context(style, after_reset: bool = False) -> Generator[None, None, None]: ...

library: Incomplete
available: Incomplete

def reload_library() -> None: ...

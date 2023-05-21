from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any, ParamSpec, TypeVar
from unittest import TestCase

P = ParamSpec("P")
T = TypeVar("T")

class param:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

InputType = (
    Iterable[str] | Iterable[Sequence[Any]] | Iterable[dict[str, Any]] | Iterable[param]
)

class parameterized:
    def __init__(
        self,
        input: InputType,
        doc_func: Callable[[Callable[..., Any], int, param], str] | None = None,
        skip_on_empty: bool = False,
    ): ...
    def __call__(self, test_func: Callable[P, T]) -> Callable[P, T]: ...
    @classmethod
    def expand(
        cls,
        input: InputType,
        name_func: Callable[[Callable[..., Any], int, param], str] | None = None,
        skip_on_empty: bool = False,
        **legacy: Any,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

_TestCaseClass = TypeVar("_TestCaseClass", bound=type[TestCase])

def parameterized_class(input: Any) -> Callable[[_TestCaseClass], _TestCaseClass]: ...

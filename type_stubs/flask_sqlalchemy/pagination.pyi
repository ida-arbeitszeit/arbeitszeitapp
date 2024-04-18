import typing as t

from _typeshed import Incomplete

class Pagination:
    page: Incomplete
    per_page: Incomplete
    max_per_page: Incomplete
    items: Incomplete
    total: Incomplete
    def __init__(
        self,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: bool = True,
        count: bool = True,
        **kwargs: t.Any,
    ) -> None: ...
    @property
    def first(self) -> int: ...
    @property
    def last(self) -> int: ...
    @property
    def pages(self) -> int: ...
    @property
    def has_prev(self) -> bool: ...
    @property
    def prev_num(self) -> int | None: ...
    def prev(self, *, error_out: bool = False) -> Pagination: ...
    @property
    def has_next(self) -> bool: ...
    @property
    def next_num(self) -> int | None: ...
    def next(self, *, error_out: bool = False) -> Pagination: ...
    def iter_pages(
        self,
        *,
        left_edge: int = 2,
        left_current: int = 2,
        right_current: int = 4,
        right_edge: int = 2,
    ) -> t.Iterator[int | None]: ...
    def __iter__(self) -> t.Iterator[t.Any]: ...

class SelectPagination(Pagination): ...
class QueryPagination(Pagination): ...

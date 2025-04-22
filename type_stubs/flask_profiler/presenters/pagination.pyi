from dataclasses import dataclass
from typing import Iterable, Iterator
from urllib.parse import ParseResult as ParseResult

from _typeshed import Incomplete
from flask_profiler.pagination import PAGE_QUERY_ARGUMENT as PAGE_QUERY_ARGUMENT

@dataclass
class Page:
    label: str
    link_target: str
    css_class: str
    @classmethod
    def is_page(self) -> bool: ...

class Gap:
    @classmethod
    def is_page(self) -> bool: ...

class Paginator:
    target_link: Incomplete
    total_page_count: Incomplete
    current_page: Incomplete
    def __init__(
        self, target_link: ParseResult, current_page: int, total_page_count: int
    ) -> None: ...
    def get_simple_pagination(self) -> Iterator[Page]: ...
    def get_truncated_pagination(self) -> Iterator[Page | Gap]: ...
    def get_pages_for_truncated_pagination(self) -> Iterable[int | None]: ...

from _typeshed import Incomplete
from flask_profiler.pagination import PAGE_QUERY_ARGUMENT as PAGE_QUERY_ARGUMENT
from typing import Iterable, Iterator, Optional, Union
from urllib.parse import ParseResult as ParseResult

class Page:
    label: str
    link_target: str
    css_class: str
    @classmethod
    def is_page(self) -> bool: ...
    def __init__(self, label, link_target, css_class) -> None: ...

class Gap:
    @classmethod
    def is_page(self) -> bool: ...

class Paginator:
    target_link: Incomplete
    total_page_count: Incomplete
    current_page: Incomplete
    def __init__(self, target_link: ParseResult, current_page: int, total_page_count: int) -> None: ...
    def get_simple_pagination(self) -> Iterator[Page]: ...
    def get_truncated_pagination(self) -> Iterator[Union[Page, Gap]]: ...
    def get_pages_for_truncated_pagination(self) -> Iterable[Optional[int]]: ...

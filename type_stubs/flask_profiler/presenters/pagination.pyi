from _typeshed import Incomplete
from flask_profiler.pagination import PAGE_QUERY_ARGUMENT as PAGE_QUERY_ARGUMENT
from typing import Iterator
from urllib.parse import ParseResult as ParseResult

class Page:
    label: str
    link_target: str
    def __init__(self, label, link_target) -> None: ...

class Paginator:
    target_link: Incomplete
    total_page_count: Incomplete
    def __init__(self, target_link: ParseResult, total_page_count: int) -> None: ...
    def __iter__(self) -> Iterator[Page]: ...

from dataclasses import dataclass

from flask_profiler.request import HttpRequest as HttpRequest

PAGE_QUERY_ARGUMENT: str

@dataclass
class PaginationContext:
    current_page: int
    page_size: int
    def get_offset(self) -> int: ...
    def get_limit(self) -> int: ...
    def get_total_pages_count(self, total_result_count: int) -> int: ...
    @classmethod
    def from_http_request(
        cls, request: HttpRequest, page_size: int = 20
    ) -> PaginationContext: ...

from dataclasses import dataclass
from urllib.parse import ParseResult as ParseResult

from flask_profiler.pagination import PaginationContext as PaginationContext
from flask_profiler.request import HttpRequest as HttpRequest
from flask_profiler.use_cases import get_summary_use_case as use_case

from . import table as table
from .formatting import format_duration_in_ms as format_duration_in_ms
from .pagination import Paginator as Paginator
from .urls import get_url_with_query as get_url_with_query

@dataclass
class ViewModel:
    table: table.Table
    pagination: Paginator
    method_filter_text: str
    name_filter_text: str
    requested_after_filter_text: str
    requested_before_filter_text: str
    submit_form_sorted_by: str

@dataclass
class GetSummaryPresenter:
    http_request: HttpRequest
    def render_summary(
        self, response: use_case.Response, pagination: PaginationContext
    ) -> ViewModel: ...
    def get_headers(self) -> list[table.Header]: ...
    def get_pagination_target_link(self) -> ParseResult: ...
    def is_currently_sorted_by(self, field: use_case.SortingField) -> bool: ...
    def alternate_sorting_order(self) -> str: ...

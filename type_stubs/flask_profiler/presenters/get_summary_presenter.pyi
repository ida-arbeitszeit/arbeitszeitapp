from . import table as table
from .formatting import format_duration_in_ms as format_duration_in_ms
from .pagination import Paginator as Paginator
from .urls import get_url_with_query as get_url_with_query
from flask_profiler.pagination import PaginationContext as PaginationContext
from flask_profiler.request import HttpRequest as HttpRequest
from flask_profiler.use_cases import get_summary_use_case as use_case
from typing import List
from urllib.parse import ParseResult as ParseResult

class ViewModel:
    table: table.Table
    pagination: Paginator
    method_filter_text: str
    name_filter_text: str
    requested_after_filter_text: str
    requested_before_filter_text: str
    submit_form_sorted_by: str
    def __init__(self, table, pagination, method_filter_text, name_filter_text, requested_after_filter_text, requested_before_filter_text, submit_form_sorted_by) -> None: ...

class GetSummaryPresenter:
    http_request: HttpRequest
    def render_summary(self, response: use_case.Response, pagination: PaginationContext) -> ViewModel: ...
    def get_headers(self) -> List[table.Header]: ...
    def get_pagination_target_link(self) -> ParseResult: ...
    def is_currently_sorted_by(self, field: use_case.SortingField) -> bool: ...
    def alternate_sorting_order(self) -> str: ...
    def __init__(self, http_request) -> None: ...

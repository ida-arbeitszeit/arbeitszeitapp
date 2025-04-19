from dataclasses import dataclass

from flask_profiler.forms import FilterFormData as FilterFormData
from flask_profiler.pagination import PaginationContext as PaginationContext
from flask_profiler.request import HttpRequest as HttpRequest
from flask_profiler.use_cases import get_summary_use_case as uc

@dataclass
class GetSummaryController:
    http_request: HttpRequest
    def process_request(self) -> uc.Request: ...
    @property
    def form_data(self) -> FilterFormData: ...
    @property
    def pagination_context(self) -> PaginationContext: ...
    def get_sorting_arguments(self) -> tuple[uc.SortingField, uc.SortingOrder]: ...

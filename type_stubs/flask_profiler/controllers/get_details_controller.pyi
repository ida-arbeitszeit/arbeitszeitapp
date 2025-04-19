from dataclasses import dataclass

from flask_profiler.forms import FilterFormData as FilterFormData
from flask_profiler.pagination import PaginationContext as PaginationContext
from flask_profiler.request import HttpRequest as HttpRequest
from flask_profiler.use_cases import get_details_use_case as use_case

@dataclass
class GetDetailsController:
    http_request: HttpRequest
    def process_request(self) -> use_case.Request: ...
    @property
    def pagination_context(self) -> PaginationContext: ...

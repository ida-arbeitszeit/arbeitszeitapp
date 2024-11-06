from dataclasses import dataclass
from typing import Optional, Protocol

from arbeitszeit.use_cases.query_companies import CompanyFilter, QueryCompaniesRequest
from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE, PAGE_PARAMETER_NAME
from arbeitszeit_web.request import Request


class QueryCompaniesFormData(Protocol):
    def get_query_string(self) -> str: ...

    def get_category_string(self) -> str: ...


_page_size = DEFAULT_PAGE_SIZE


@dataclass
class QueryCompaniesController:
    request: Request

    def import_form_data(
        self,
        form: Optional[QueryCompaniesFormData] = None,
    ) -> QueryCompaniesRequest:
        if form is None:
            filter_category = CompanyFilter.by_name
            query = None
        else:
            query = form.get_query_string().strip() or None
            if form.get_category_string() == "Email":
                filter_category = CompanyFilter.by_email
            else:
                filter_category = CompanyFilter.by_name
        offset = self._get_pagination_offset()
        return QueryCompaniesRequest(
            query_string=query,
            filter_category=filter_category,
            offset=offset,
            limit=_page_size,
        )

    def _get_pagination_offset(self) -> int:
        page_str = self.request.query_string().get_last_value(PAGE_PARAMETER_NAME)
        if page_str is None:
            return 0
        try:
            page_number = int(page_str)
        except ValueError:
            return 0
        return (page_number - 1) * _page_size

from dataclasses import dataclass
from typing import Optional, Protocol

from arbeitszeit.use_cases.query_companies import CompanyFilter, QueryCompaniesRequest
from arbeitszeit_web.pagination import PAGE_PARAMETER_NAME
from arbeitszeit_web.request import Request


class QueryCompaniesFormData(Protocol):
    def get_query_string(self) -> str:
        ...

    def get_category_string(self) -> str:
        ...


_PAGE_SIZE = 15


@dataclass
class QueryCompaniesRequestImpl(QueryCompaniesRequest):
    query: Optional[str]
    filter_category: CompanyFilter
    offset: Optional[int]
    limit: Optional[int]

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> CompanyFilter:
        return self.filter_category

    def get_offset(self) -> Optional[int]:
        return self.offset

    def get_limit(self) -> Optional[int]:
        return self.limit


class QueryCompaniesController:
    def import_form_data(
        self,
        form: Optional[QueryCompaniesFormData] = None,
        request: Optional[Request] = None,
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
        offset = self._get_pagination_offset(request) if request else 0
        return QueryCompaniesRequestImpl(
            query=query,
            filter_category=filter_category,
            offset=offset,
            limit=_PAGE_SIZE,
        )

    def _get_pagination_offset(self, request: Request) -> int:
        page_str = request.query_string().get(PAGE_PARAMETER_NAME)
        if page_str is None:
            return 0
        try:
            page_number = int(page_str)
        except ValueError:
            return 0
        return (page_number - 1) * _PAGE_SIZE

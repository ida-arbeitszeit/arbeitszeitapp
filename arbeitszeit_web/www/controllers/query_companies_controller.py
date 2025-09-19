from typing import Optional, Protocol

from arbeitszeit.interactors.query_companies import CompanyFilter, QueryCompaniesRequest
from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE, calculate_current_offset
from arbeitszeit_web.request import Request


class QueryCompaniesFormData(Protocol):
    def get_query_string(self) -> str: ...

    def get_category_string(self) -> str: ...


class QueryCompaniesController:
    def import_form_data(
        self,
        *,
        request: Request,
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
        offset = calculate_current_offset(request=request, limit=DEFAULT_PAGE_SIZE)
        return QueryCompaniesRequest(
            query_string=query,
            filter_category=filter_category,
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )

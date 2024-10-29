from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueryPlansRequest,
)
from arbeitszeit_web.pagination import PAGE_PARAMETER_NAME, Pagination, Paginator
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator

from .notification import Notifier
from .url_index import UrlIndex, UserUrlIndex


class NotAnIntegerError(ValueError):
    pass


class QueryPlansFormData(Protocol):
    def get_query_string(self) -> str: ...

    def get_category_string(self) -> str: ...

    def get_radio_string(self) -> str: ...

    def get_checkbox_value(self) -> bool: ...


_PAGE_SIZE = 15


@dataclass
class QueryPlansController:
    def import_form_data(
        self,
        form: Optional[QueryPlansFormData] = None,
        request: Optional[Request] = None,
    ) -> QueryPlansRequest:
        if form is None:
            query = None
            filter_category = PlanFilter.by_product_name
            sorting_category = PlanSorting.by_activation
            include_expired_plans = False
        else:
            query = form.get_query_string().strip() or None
            filter_category = self._import_filter_category(form)
            sorting_category = self._import_sorting_category(form)
            include_expired_plans = self._import_include_expired(form)
        offset = self._get_pagination_offset(request) if request else 0
        return QueryPlansRequest(
            query_string=query,
            filter_category=filter_category,
            sorting_category=sorting_category,
            include_expired_plans=include_expired_plans,
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

    def _import_filter_category(self, form: QueryPlansFormData) -> PlanFilter:
        if form.get_category_string() == "Plan-ID":
            filter_category = PlanFilter.by_plan_id
        else:
            filter_category = PlanFilter.by_product_name
        return filter_category

    def _import_sorting_category(self, form: QueryPlansFormData) -> PlanSorting:
        sorting = form.get_radio_string()
        if sorting == "company_name":
            sorting_category = PlanSorting.by_company_name
        else:
            sorting_category = PlanSorting.by_activation
        return sorting_category

    def _import_include_expired(self, form: QueryPlansFormData) -> bool:
        return form.get_checkbox_value()


@dataclass
class ResultTableRow:
    plan_details_url: str
    company_summary_url: str
    company_name: str
    product_name: str
    description: str
    price_per_unit: str
    is_public_service: bool
    is_cooperating: bool
    is_expired: bool


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryPlansViewModel:
    results: ResultsTable
    show_results: bool
    pagination: Pagination

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryPlansPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex
    user_notifier: Notifier
    trans: Translator
    session: Session

    def present(
        self, response: PlanQueryResponse, request: Request
    ) -> QueryPlansViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.trans.gettext("No results."))
        paginator = self._create_paginator(
            request,
            total_results=response.total_results,
            current_offset=response.request.offset or 0,
        )
        return QueryPlansViewModel(
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        plan_details_url=self.user_url_index.get_plan_details_url(
                            result.plan_id
                        ),
                        company_summary_url=self.url_index.get_company_summary_url(
                            company_id=result.company_id,
                        ),
                        company_name=result.company_name,
                        product_name=result.product_name,
                        description="".join(result.description.splitlines())[:150],
                        price_per_unit=str(round(result.price_per_unit, 2)),
                        is_public_service=result.is_public_service,
                        is_cooperating=result.is_cooperating,
                        is_expired=result.is_expired,
                    )
                    for result in response.results
                ],
            ),
            pagination=Pagination(
                is_visible=paginator.page_count > 1,
                pages=paginator.get_pages(),
            ),
        )

    def get_empty_view_model(self) -> QueryPlansViewModel:
        return QueryPlansViewModel(
            results=ResultsTable(rows=[]),
            show_results=False,
            pagination=Pagination(is_visible=False, pages=[]),
        )

    def _create_paginator(
        self, request: Request, total_results: int, current_offset: int
    ) -> Paginator:
        return Paginator(
            base_url=self._get_pagination_base_url(),
            query_arguments=dict(request.query_string().items()),
            page_size=_PAGE_SIZE,
            total_results=total_results,
            current_offset=current_offset,
        )

    def _get_pagination_base_url(self) -> str:
        return self.url_index.get_query_plans_url()

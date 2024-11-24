from dataclasses import dataclass

from arbeitszeit.use_cases.query_plans import PlanQueryResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE, Pagination, Paginator
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex, UserUrlIndex


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
    rows: list[ResultTableRow]


@dataclass
class QueryPlansViewModel:
    total_results: int
    results: ResultsTable
    show_results: bool
    pagination: Pagination


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
            total_results=response.total_results,
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
            total_results=0,
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
            page_size=DEFAULT_PAGE_SIZE,
            total_results=total_results,
            current_offset=current_offset,
        )

    def _get_pagination_base_url(self) -> str:
        return self.url_index.get_query_plans_url()

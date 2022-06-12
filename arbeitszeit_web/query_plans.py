from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    QueryPlansRequest,
)
from arbeitszeit_web.translator import Translator

from .notification import Notifier
from .url_index import CompanySummaryUrlIndex, PlanSummaryUrlIndex


class QueryPlansFormData(Protocol):
    def get_query_string(self) -> str:
        ...

    def get_category_string(self) -> str:
        ...


@dataclass
class QueryPlansRequestImpl(QueryPlansRequest):
    query: Optional[str]
    filter_category: PlanFilter

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> PlanFilter:
        return self.filter_category


class QueryPlansController:
    def import_form_data(self, form: Optional[QueryPlansFormData]) -> QueryPlansRequest:
        if form is None:
            filter_category = PlanFilter.by_product_name
            query = None
        else:
            query = form.get_query_string().strip() or None
            if form.get_category_string() == "Plan-ID":
                filter_category = PlanFilter.by_plan_id
            else:
                filter_category = PlanFilter.by_product_name
        return QueryPlansRequestImpl(query=query, filter_category=filter_category)


@dataclass
class ResultTableRow:
    plan_summary_url: str
    company_summary_url: str
    company_name: str
    product_name: str
    description: str
    price_per_unit: str
    is_public_service: bool
    is_available: bool
    is_cooperating: bool


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryPlansViewModel:
    results: ResultsTable
    show_results: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryPlansPresenter:
    plan_url_index: PlanSummaryUrlIndex
    company_url_index: CompanySummaryUrlIndex
    user_notifier: Notifier
    trans: Translator

    def present(self, response: PlanQueryResponse) -> QueryPlansViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.trans.gettext("No results."))
        return QueryPlansViewModel(
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        plan_summary_url=self.plan_url_index.get_plan_summary_url(
                            result.plan_id
                        ),
                        company_summary_url=self.company_url_index.get_company_summary_url(
                            result.company_id
                        ),
                        company_name=result.company_name,
                        product_name=result.product_name,
                        description="".join(result.description.splitlines())[:150],
                        price_per_unit=str(round(result.price_per_unit, 2)),
                        is_public_service=result.is_public_service,
                        is_available=result.is_available,
                        is_cooperating=result.is_cooperating,
                    )
                    for result in response.results
                ],
            ),
        )

    def get_empty_view_model(self) -> QueryPlansViewModel:
        return QueryPlansViewModel(
            results=ResultsTable(rows=[]),
            show_results=False,
        )

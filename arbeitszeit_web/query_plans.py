from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    QueryPlansRequest,
)


class PlanSummaryUrlIndex(Protocol):
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        ...


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
class Notification:
    text: str


@dataclass
class ResultTableRow:
    plan_id: str
    plan_summary_url: str
    company_name: str
    product_name: str
    description: List[str]
    price_per_unit: str
    type_of_plan: str
    ends_in: str
    is_available: bool


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryPlansViewModel:
    notifications: List[Notification]
    results: ResultsTable
    show_results: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryPlansPresenter:
    plan_summary_url_index: PlanSummaryUrlIndex

    def present(self, response: PlanQueryResponse) -> QueryPlansViewModel:
        if response.results:
            notifications = []
        else:
            notifications = [Notification(text="Keine Ergebnisse!")]
        return QueryPlansViewModel(
            notifications=notifications,
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        plan_id=str(result.plan_id),
                        plan_summary_url=self.plan_summary_url_index.get_plan_summary_url(
                            result.plan_id
                        ),
                        company_name=result.company_name,
                        product_name=result.product_name,
                        description=result.description.splitlines(),
                        price_per_unit=str(round(result.price_per_unit, 2)),
                        type_of_plan="Öffentlich"
                        if result.is_public_service
                        else "Produktiv",
                        ends_in=f"{result.expiration_relative} Tage"
                        if result.expiration_relative is not None
                        else "–",
                        is_available=result.is_available,
                    )
                    for result in response.results
                ],
            ),
        )

    def get_empty_view_model(self) -> QueryPlansViewModel:
        return QueryPlansViewModel(
            notifications=[],
            results=ResultsTable(rows=[]),
            show_results=False,
        )

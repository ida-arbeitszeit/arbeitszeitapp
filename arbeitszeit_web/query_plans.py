from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol

from injector import inject

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueryPlansRequest,
)
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator

from .notification import Notifier
from .url_index import UrlIndex, UserUrlIndex


class QueryPlansFormData(Protocol):
    def get_query_string(self) -> str:
        ...

    def get_category_string(self) -> str:
        ...

    def get_radio_string(self) -> str:
        ...


class QueryPlansController:
    def import_form_data(self, form: Optional[QueryPlansFormData]) -> QueryPlansRequest:
        if form is None:
            query = None
            filter_category = PlanFilter.by_product_name
            sorting_category = PlanSorting.by_activation
        else:
            query = form.get_query_string().strip() or None
            filter_category = self._import_filter_category(form)
            sorting_category = self._import_sorting_category(form)
        return QueryPlansRequest(
            query_string=query,
            filter_category=filter_category,
            sorting_category=sorting_category,
        )

    def _import_filter_category(self, form: QueryPlansFormData) -> PlanFilter:
        if form.get_category_string() == "Plan-ID":
            filter_category = PlanFilter.by_plan_id
        else:
            filter_category = PlanFilter.by_product_name
        return filter_category

    def _import_sorting_category(self, form: QueryPlansFormData) -> PlanSorting:
        sorting = form.get_radio_string()
        if sorting == "price":
            sorting_category = PlanSorting.by_price
        elif sorting == "company_name":
            sorting_category = PlanSorting.by_company_name
        else:
            sorting_category = PlanSorting.by_activation
        return sorting_category


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


@inject
@dataclass
class QueryPlansPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex
    user_notifier: Notifier
    trans: Translator
    session: Session

    def present(self, response: PlanQueryResponse) -> QueryPlansViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.trans.gettext("No results."))
        return QueryPlansViewModel(
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        plan_summary_url=self.user_url_index.get_plan_summary_url(
                            result.plan_id
                        ),
                        company_summary_url=self.url_index.get_company_summary_url(
                            user_role=self.session.get_user_role(),
                            company_id=result.company_id,
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

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from flask import Markup

from arbeitszeit.use_cases.query_products import (
    ProductFilter,
    ProductQueryResponse,
    QueryProductsRequest,
)

from .prepare_strings_for_html import text_to_html


class PlanSummaryUrlIndex(Protocol):
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        ...


class QueryProductsFormData(Protocol):
    def get_query_string(self) -> str:
        ...

    def get_category_string(self) -> str:
        ...


@dataclass
class QueryProductsRequestImpl(QueryProductsRequest):
    query: Optional[str]
    filter_category: ProductFilter

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> ProductFilter:
        return self.filter_category


class QueryProductsController:
    def import_form_data(
        self, form: Optional[QueryProductsFormData]
    ) -> QueryProductsRequest:
        if form is None:
            filter_category = ProductFilter.by_name
            query = None
        else:
            query = form.get_query_string().strip() or None
            if form.get_category_string() == "Beschreibung":
                filter_category = ProductFilter.by_description
            else:
                filter_category = ProductFilter.by_name
        return QueryProductsRequestImpl(query=query, filter_category=filter_category)


@dataclass
class Notification:
    text: str


@dataclass
class ResultTableRow:
    plan_id: str
    plan_summary_url: str
    product_name: str
    seller_name: str
    product_description: Markup
    price_per_unit: str
    is_public_service: str
    contact_email: str


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryProductsViewModel:
    notifications: List[Notification]
    results: ResultsTable
    show_results: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryProductsPresenter:
    plan_summary_url_index: PlanSummaryUrlIndex

    def present(self, response: ProductQueryResponse) -> QueryProductsViewModel:
        if response.results:
            notifications = []
        else:
            notifications = [Notification(text="Keine Ergebnisse!")]
        return QueryProductsViewModel(
            notifications=notifications,
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        plan_id=str(result.plan_id),
                        plan_summary_url=self.plan_summary_url_index.get_plan_summary_url(
                            result.plan_id
                        ),
                        product_name=result.product_name,
                        seller_name=result.seller_name,
                        product_description=text_to_html(result.product_description),
                        price_per_unit=f"{result.price_per_unit} Std.",
                        is_public_service="Öffentlich"
                        if result.is_public_service
                        else "Produktiv",
                        contact_email=f"mailto:{result.seller_email}",
                    )
                    for result in response.results
                ],
            ),
        )

    def get_empty_view_model(self) -> QueryProductsViewModel:
        return QueryProductsViewModel(
            notifications=[],
            results=ResultsTable(rows=[]),
            show_results=False,
        )

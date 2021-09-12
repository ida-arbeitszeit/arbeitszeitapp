from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from arbeitszeit.use_cases.query_products import ProductQueryResponse


@dataclass
class Notification:
    text: str


@dataclass
class ResultTableRow:
    plan_id: str
    product_name: str
    seller_name: str
    product_description: str
    price_per_unit: str
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


class QueryProductsPresenter:
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
                        product_name=result.product_name,
                        seller_name=result.seller_name,
                        product_description=result.product_description,
                        price_per_unit=f"{result.price_per_unit} Std.",
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

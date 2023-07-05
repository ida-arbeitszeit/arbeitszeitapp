from dataclasses import dataclass
from typing import Iterable, List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.query_member_purchases import PurchaseQueryResponse


@dataclass
class MemberPurchasesPresenter:
    @dataclass
    class ViewModel:
        @dataclass
        class Purchase:
            purchase_date: str
            product_name: str
            product_description: str
            price_per_unit: str
            purchase_amount: str
            price_total: str

        is_purchases_visible: bool
        purchases: List[Purchase]

    datetime_service: DatetimeService

    def present_member_purchases(
        self, use_case_response: Iterable[PurchaseQueryResponse]
    ) -> ViewModel:
        purchases = list(use_case_response)
        return self.ViewModel(
            is_purchases_visible=bool(purchases),
            purchases=[
                self.ViewModel.Purchase(
                    purchase_date=self.datetime_service.format_datetime(
                        date=purchase.purchase_date,
                        fmt="%d.%m.%Y",
                    ),
                    product_name=purchase.product_name,
                    product_description=purchase.product_description,
                    price_per_unit=str(purchase.price_per_unit),
                    purchase_amount=str(purchase.amount),
                    price_total=str(purchase.price_total),
                )
                for purchase in purchases
            ],
        )

from dataclasses import dataclass
from typing import Iterator, List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.query_company_purchases import PurchaseQueryResponse
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    @dataclass
    class Purchase:
        purchase_date: str
        product_name: str
        product_description: str
        purpose: str
        price_per_unit: str
        amount: str
        price_total: str

    purchases: List[Purchase]
    show_purchases: bool


@dataclass
class CompanyPurchasesPresenter:
    datetime_service: DatetimeService
    translator: Translator

    def present(self, use_case_response: Iterator[PurchaseQueryResponse]) -> ViewModel:
        purchases = [self._format_purchase(purchase) for purchase in use_case_response]
        show_purchases = True if (len(purchases) > 0) else False
        return ViewModel(purchases=purchases, show_purchases=show_purchases)

    def _format_purchase(self, purchase: PurchaseQueryResponse) -> ViewModel.Purchase:
        return ViewModel.Purchase(
            purchase_date=self.datetime_service.format_datetime(
                date=purchase.purchase_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            product_name=purchase.product_name,
            product_description=purchase.product_description,
            purpose=self._format_purpose(purchase.purpose),
            price_per_unit=str(round(purchase.price_per_unit, 2)),
            amount=str(purchase.amount),
            price_total=str(round(purchase.price_total, 2)),
        )

    def _format_purpose(self, purpose: PurposesOfPurchases) -> str:
        if purpose == PurposesOfPurchases.raw_materials:
            return self.translator.gettext("Liquid means of production")
        else:
            return self.translator.gettext("Fixed means of production")

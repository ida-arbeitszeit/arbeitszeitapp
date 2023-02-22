from dataclasses import dataclass, field
from typing import Iterator

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.query_purchases import PurchaseQueryResponse
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

    datetime_service: DatetimeService
    translator: Translator
    purchases: list[Purchase] = field(default_factory=list)

    def append(self, purchase_respond: PurchaseQueryResponse) -> None:

        p = self.Purchase(
            purchase_date=self.datetime_service.format_datetime(
                date=purchase_respond.purchase_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            product_name=purchase_respond.product_name,
            product_description=purchase_respond.product_description,
            purpose=self._convert_purpose(purchase_respond.purpose),
            price_per_unit=str(round(purchase_respond.price_per_unit, 2)),
            amount=str(purchase_respond.amount),
            price_total=str(round(purchase_respond.price_total, 2)),
        )
        self.purchases.append(p)

    def _convert_purpose(self, purpose: PurposesOfPurchases) -> str:
        if purpose == PurposesOfPurchases.raw_materials:
            return self.translator.gettext("Liquid means of production")
        elif purpose == PurposesOfPurchases.means_of_prod:
            return self.translator.gettext("Fixed means of production")
        else:
            return self.translator.gettext("Consumption")

    def __len__(self) -> int:
        return len(self.purchases)

    def __iter__(self) -> Iterator[Purchase]:
        yield from self.purchases


@dataclass
class CompanyPurchasesPresenter:
    datetime_service: DatetimeService
    translator: Translator

    def present(self, use_case_response: Iterator[PurchaseQueryResponse]) -> ViewModel:
        model = ViewModel(self.datetime_service, self.translator)

        for p in use_case_response:
            model.append(p)

        return model

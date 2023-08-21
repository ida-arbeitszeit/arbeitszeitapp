from dataclasses import dataclass
from typing import Iterator, List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import PurposesOfPurchases
from arbeitszeit.use_cases.query_company_consumptions import ConsumptionQueryResponse
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    @dataclass
    class Consumption:
        consumption_date: str
        product_name: str
        product_description: str
        purpose: str
        price_per_unit: str
        amount: str
        price_total: str

    consumptions: List[Consumption]
    show_consumptions: bool


@dataclass
class CompanyConsumptionsPresenter:
    datetime_service: DatetimeService
    translator: Translator

    def present(
        self, use_case_response: Iterator[ConsumptionQueryResponse]
    ) -> ViewModel:
        consumptions = [
            self._format_consumption(consumption) for consumption in use_case_response
        ]
        show_consumptions = True if (len(consumptions) > 0) else False
        return ViewModel(consumptions=consumptions, show_consumptions=show_consumptions)

    def _format_consumption(
        self, purchase: ConsumptionQueryResponse
    ) -> ViewModel.Consumption:
        return ViewModel.Consumption(
            consumption_date=self.datetime_service.format_datetime(
                date=purchase.consumption_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            product_name=purchase.product_name,
            product_description=purchase.product_description,
            purpose=self._format_purpose(purchase.purpose),
            price_per_unit=str(round(purchase.price_per_unit, 2)),
            amount=str(purchase.amount),
            price_total=str(round(purchase.price_per_unit * purchase.amount, 2)),
        )

    def _format_purpose(self, purpose: PurposesOfPurchases) -> str:
        if purpose == PurposesOfPurchases.raw_materials:
            return self.translator.gettext("Liquid means of production")
        else:
            return self.translator.gettext("Fixed means of production")

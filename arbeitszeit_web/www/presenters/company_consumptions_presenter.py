from dataclasses import dataclass
from typing import Iterator, List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import ConsumptionType
from arbeitszeit.use_cases.query_company_consumptions import ConsumptionQueryResponse
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    @dataclass
    class Consumption:
        consumption_date: str
        product_name: str
        product_description: str
        consumption_type: str
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
        self, consumption: ConsumptionQueryResponse
    ) -> ViewModel.Consumption:
        return ViewModel.Consumption(
            consumption_date=self.datetime_service.format_datetime(
                date=consumption.consumption_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            product_name=consumption.product_name,
            product_description=consumption.product_description,
            consumption_type=self._format_consumption_type(
                consumption.consumption_type
            ),
            price_per_unit=str(round(consumption.price_per_unit, 2)),
            amount=str(consumption.amount),
            price_total=str(round(consumption.price_per_unit * consumption.amount, 2)),
        )

    def _format_consumption_type(self, consumption_type: ConsumptionType) -> str:
        if consumption_type == ConsumptionType.raw_materials:
            return self.translator.gettext("Liquid means of production")
        else:
            return self.translator.gettext("Fixed means of production")

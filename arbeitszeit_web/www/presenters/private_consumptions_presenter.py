from dataclasses import dataclass
from typing import Iterable, List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.query_private_consumptions import (
    PrivateConsumptionsQueryResponse,
)


@dataclass
class PrivateConsumptionsPresenter:
    @dataclass
    class ViewModel:
        @dataclass
        class Consumption:
            consumption_date: str
            product_name: str
            product_description: str
            price_per_unit: str
            consumption_amount: str
            price_total: str

        is_consumptions_visible: bool
        consumptions: List[Consumption]

    datetime_service: DatetimeService

    def present_private_consumptions(
        self, use_case_response: Iterable[PrivateConsumptionsQueryResponse]
    ) -> ViewModel:
        consumptions = list(use_case_response)
        return self.ViewModel(
            is_consumptions_visible=bool(consumptions),
            consumptions=[
                self.ViewModel.Consumption(
                    consumption_date=self.datetime_service.format_datetime(
                        date=consumption.consumption_date,
                        fmt="%d.%m.%Y",
                    ),
                    product_name=consumption.product_name,
                    product_description=consumption.product_description,
                    price_per_unit=str(consumption.price_per_unit),
                    consumption_amount=str(consumption.amount),
                    price_total=str(consumption.price_total),
                )
                for consumption in consumptions
            ],
        )

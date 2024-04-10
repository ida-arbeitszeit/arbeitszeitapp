from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.query_private_consumptions import Response
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter


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

    datetime_formatter: DatetimeFormatter

    def present_private_consumptions(self, response: Response) -> ViewModel:
        return self.ViewModel(
            is_consumptions_visible=bool(response.consumptions),
            consumptions=[
                self.ViewModel.Consumption(
                    consumption_date=self.datetime_formatter.format_datetime(
                        date=consumption.consumption_date,
                        fmt="%d.%m.%Y",
                    ),
                    product_name=consumption.product_name,
                    product_description=consumption.product_description,
                    price_per_unit=str(consumption.price_per_unit),
                    consumption_amount=str(consumption.amount),
                    price_total=str(consumption.price_total),
                )
                for consumption in response.consumptions
            ],
        )

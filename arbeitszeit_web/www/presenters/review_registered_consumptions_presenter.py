from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.review_registered_consumptions import RegisteredConsumption
from arbeitszeit.use_cases.review_registered_consumptions import (
    ReviewRegisteredConsumptionsUseCase as UseCase,
)
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class Consumption:
    date: str
    consumer_name: str
    consumer_url: Optional[str]
    consumer_type_icon: str
    product_name: str
    plan_url: str
    labour_hours_consumed: str


@dataclass
class ViewModel:
    consumptions: list[Consumption]


@dataclass
class ReviewRegisteredConsumptionsPresenter:
    datetime_formatter: DatetimeFormatter
    url_index: UrlIndex

    def present(self, use_case_response: UseCase.Response) -> ViewModel:
        consumptions = [
            self._create_consumption(consumption)
            for consumption in use_case_response.consumptions
        ]
        return ViewModel(consumptions=consumptions)

    def _create_consumption(self, consumption: RegisteredConsumption) -> Consumption:
        return Consumption(
            date=self.datetime_formatter.format_datetime(consumption.date),
            consumer_name=consumption.consumer_name,
            consumer_url=self._get_consumer_url(consumption),
            consumer_type_icon=self._get_consumer_type_icon(consumption),
            product_name=consumption.product_name,
            plan_url=self.url_index.get_plan_details_url(
                plan_id=consumption.plan_id, user_role=UserRole.company
            ),
            labour_hours_consumed=str(round(consumption.labour_hours_consumed, 2)),
        )

    def _get_consumer_url(self, consumption: RegisteredConsumption) -> Optional[str]:
        if consumption.is_private_consumption:
            return None
        else:
            return self.url_index.get_company_summary_url(consumption.consumer_id)

    def _get_consumer_type_icon(self, consumption: RegisteredConsumption) -> str:
        if consumption.is_private_consumption:
            return "user"
        else:
            return "industry"

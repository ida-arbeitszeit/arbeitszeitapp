from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.start_page import StartPageUseCase
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter


@dataclass
class StartPagePresenter:
    @dataclass
    class Plan:
        prd_name: str
        activation_date: str
        rejection_date: str

    @dataclass
    class ViewModel:
        show_plans: bool
        plans: List[StartPagePresenter.Plan]

    datetime_formatter: DatetimeFormatter

    def show_start_page(self, response: StartPageUseCase.Response) -> ViewModel:
        if not response.latest_plans:
            return StartPagePresenter.ViewModel(show_plans=False, plans=[])
        return self.ViewModel(
            show_plans=True,
            plans=[
                self.Plan(
                    prd_name=plan.product_name,
                    activation_date=self.datetime_formatter.format_datetime(
                        plan.activation_date, zone="Europe/Berlin", fmt="%d.%m."
                    ),
                    rejection_date=self.datetime_formatter.format_datetime(
                        plan.activation_date, zone="Europe/Berlin", fmt="%d.%m."
                    ),
                )
                for plan in response.latest_plans
            ],
        )

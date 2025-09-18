from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors.start_page import StartPageInteractor
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter


@dataclass
class StartPagePresenter:
    @dataclass
    class Plan:
        prd_name: str
        approval_date: str

    @dataclass
    class ViewModel:
        show_plans: bool
        plans: List[StartPagePresenter.Plan]

    datetime_formatter: DatetimeFormatter

    def show_start_page(self, response: StartPageInteractor.Response) -> ViewModel:
        if not response.latest_plans:
            return StartPagePresenter.ViewModel(show_plans=False, plans=[])
        return self.ViewModel(
            show_plans=True,
            plans=[
                self.Plan(
                    prd_name=plan.product_name,
                    approval_date=self.datetime_formatter.format_datetime(
                        plan.approval_date, fmt="%d.%m."
                    ),
                )
                for plan in response.latest_plans
            ],
        )

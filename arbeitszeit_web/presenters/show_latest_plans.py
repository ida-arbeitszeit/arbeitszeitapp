from __future__ import annotations

from dataclasses import dataclass
from typing import List

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.show_latest_plans import ShowLatestPlans


@inject
@dataclass
class ShowLatestPlansPresenter:
    @dataclass
    class Plan:
        prd_name: str
        activation_date: str

    @dataclass
    class ViewModel:
        has_plans: bool
        plans: List[ShowLatestPlansPresenter.Plan]

    datetime_service: DatetimeService

    def show_plans(self, response: ShowLatestPlans.Response) -> ViewModel:
        if not response.latest_plans:
            return ShowLatestPlansPresenter.ViewModel(has_plans=False, plans=[])
        return self.ViewModel(
            has_plans=True,
            plans=[
                self.Plan(
                    prd_name=plan.product_name,
                    activation_date=self.datetime_service.format_datetime(
                        plan.activation_date, zone="Europe/Berlin", fmt="%d.%m."
                    ),
                )
                for plan in response.latest_plans
            ],
        )

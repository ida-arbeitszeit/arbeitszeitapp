from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from injector import inject
from arbeitszeit.entities import Plan

from arbeitszeit.repositories import PlanRepository


@dataclass
class ShowMyPlansRequest:
    company_id: UUID


@dataclass
class ShowMyPlansResponse:
    all_plans: List[Plan]


@inject
@dataclass
class ShowMyPlansUseCase:
    plan_repository: PlanRepository

    def __call__(self, request: ShowMyPlansRequest) -> ShowMyPlansResponse:
        all_plans = [
            plan
            for plan in self.plan_repository.get_all_plans_for_company(
                request.company_id
            )
        ]
        return ShowMyPlansResponse(all_plans=all_plans)

from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from uuid import UUID

from injector import inject

from arbeitszeit.plan_summary import PlanSummary, PlanSummaryService
from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class GetPlanSummaryMember:
    @dataclass
    class Success:
        plan_summary: PlanSummary

    @dataclass
    class Failure:
        pass

    plan_repository: PlanRepository
    plan_summary_service: PlanSummaryService

    def __call__(self, plan_id: UUID) -> Union[Success, Failure]:
        plan = self.plan_repository.get_all_plans().with_id(plan_id).first()
        if plan is None:
            return self.Failure()
        return self.Success(
            plan_summary=self.plan_summary_service.get_summary_from_plan(plan)
        )

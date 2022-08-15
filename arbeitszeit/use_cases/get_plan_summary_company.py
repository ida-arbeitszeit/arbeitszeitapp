from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from uuid import UUID

from injector import inject

from arbeitszeit.plan_summary import PlanSummary, PlanSummaryService
from arbeitszeit.repositories import CompanyRepository, PlanRepository


@inject
@dataclass
class GetPlanSummaryCompany:
    @dataclass
    class Success:
        plan_summary: PlanSummary
        current_user_is_planner: bool

    @dataclass
    class Failure:
        pass

    plan_repository: PlanRepository
    company_repository: CompanyRepository
    plan_summary_service: PlanSummaryService

    def get_plan_summary_for_company(
        self, plan_id: UUID, company_id: UUID
    ) -> Union[Success, Failure]:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        company = self.company_repository.get_by_id(company_id)
        if plan is None:
            return self.Failure()
        assert company
        return self.Success(
            plan_summary=self.plan_summary_service.get_summary_from_plan(plan),
            current_user_is_planner=(plan.planner == company),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.plan_summary import PlanSummary, PlanSummaryService
from arbeitszeit.repositories import CompanyRepository, PlanRepository


@inject
@dataclass
class GetPlanSummaryCompany:
    @dataclass
    class Response:
        plan_summary: Optional[PlanSummary]
        current_user_is_planner: bool

    plan_repository: PlanRepository
    company_repository: CompanyRepository
    plan_summary_service: PlanSummaryService

    def get_plan_summary_for_company(self, plan_id: UUID, company_id: UUID) -> Response:
        plan = self.plan_repository.get_plans().with_id(plan_id).first()
        company = (
            self.company_repository.get_all_companies().with_id(company_id).first()
        )
        if plan is None:
            return self.Response(
                plan_summary=None,
                current_user_is_planner=False,
            )
        assert company
        return self.Response(
            plan_summary=self.plan_summary_service.get_summary_from_plan(plan),
            current_user_is_planner=(plan.planner == company),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.plan_summary import PlanSummary, PlanSummaryService
from arbeitszeit.repositories import CompanyRepository, DatabaseGateway


@dataclass
class GetPlanSummaryCompany:
    @dataclass
    class Response:
        plan_summary: Optional[PlanSummary]
        current_user_is_planner: bool

    database_gateway: DatabaseGateway
    company_repository: CompanyRepository
    plan_summary_service: PlanSummaryService

    def get_plan_summary_for_company(self, plan_id: UUID, company_id: UUID) -> Response:
        plan_summary = self.plan_summary_service.get_summary_from_plan(plan_id)
        if plan_summary is None:
            return self.Response(
                plan_summary=None,
                current_user_is_planner=False,
            )
        plan = self.database_gateway.get_plans().with_id(plan_id).first()
        assert plan  # exists because plan_summary exists
        return self.Response(
            plan_summary=plan_summary,
            current_user_is_planner=(plan.planner == company_id),
        )

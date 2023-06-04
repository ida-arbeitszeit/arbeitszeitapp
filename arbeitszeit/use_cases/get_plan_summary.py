from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.plan_summary import PlanSummary, PlanSummaryService


@dataclass
class GetPlanSummaryUseCase:
    @dataclass
    class Request:
        plan_id: UUID

    @dataclass
    class Response:
        plan_summary: PlanSummary

    plan_summary_service: PlanSummaryService

    def get_plan_summary(self, request: Request) -> Optional[Response]:
        plan_summary = self.plan_summary_service.get_summary_from_plan(request.plan_id)
        if plan_summary is None:
            return None
        return self.Response(plan_summary=plan_summary)

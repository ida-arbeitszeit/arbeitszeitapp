from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.plan_details import PlanDetails, PlanDetailsService


@dataclass
class GetPlanDetailsUseCase:
    @dataclass
    class Request:
        plan_id: UUID

    @dataclass
    class Response:
        plan_details: PlanDetails

    plan_details_service: PlanDetailsService

    def get_plan_details(self, request: Request) -> Optional[Response]:
        plan_details = self.plan_details_service.get_details_from_plan(request.plan_id)
        if plan_details is None:
            return None
        return self.Response(plan_details=plan_details)

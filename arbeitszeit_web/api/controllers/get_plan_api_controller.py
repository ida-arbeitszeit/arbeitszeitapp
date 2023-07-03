from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit_web.api.presenters.response_errors import BadRequest


@dataclass
class GetPlanApiController:
    def create_request(self, plan_id: str) -> GetPlanSummaryUseCase.Request:
        plan_id = plan_id.strip()
        try:
            plan_uuid = UUID(plan_id)
        except ValueError:
            raise BadRequest(f"Plan id must be in UUID format, got {plan_id}.")
        return GetPlanSummaryUseCase.Request(plan_uuid)

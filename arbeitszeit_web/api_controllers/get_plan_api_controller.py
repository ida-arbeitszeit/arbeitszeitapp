from dataclasses import dataclass
from uuid import UUID

from arbeitszeit_web.api_presenters.response_errors import BadRequest


@dataclass
class GetPlanApiController:
    def format_input(self, plan_id: str) -> UUID:
        plan_id = plan_id.strip()
        try:
            plan_uuid = UUID(plan_id)
        except ValueError:
            raise BadRequest(f"Plan id must be in UUID format, got {plan_id}.")
        return plan_uuid

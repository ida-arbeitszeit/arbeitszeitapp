from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit_web.api.controllers.parameters import PathParameter
from arbeitszeit_web.api.response_errors import BadRequest

plan_detail_expected_input = [
    PathParameter(
        name="plan_id",
        description="The plan id.",
    )
]


@dataclass
class GetPlanApiController:
    def create_request(self, plan_id: str) -> GetPlanDetailsInteractor.Request:
        plan_id = plan_id.strip()
        try:
            plan_uuid = UUID(plan_id)
        except ValueError:
            raise BadRequest(f"Plan id must be in UUID format, got {plan_id}.")
        return GetPlanDetailsInteractor.Request(plan_uuid)

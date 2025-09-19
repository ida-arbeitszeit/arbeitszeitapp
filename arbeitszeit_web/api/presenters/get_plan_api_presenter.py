from typing import Optional

from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit.plan_details import PlanDetails
from arbeitszeit_web.api.presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
    JsonValue,
)
from arbeitszeit_web.api.response_errors import NotFound


class GetPlanApiPresenter:
    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonObject(
            members=dict(
                plan_id=JsonString(),
                is_active=JsonBoolean(),
                planner_id=JsonString(),
                planner_name=JsonString(),
                product_name=JsonString(),
                description=JsonString(),
                timeframe=JsonInteger(),
                active_days=JsonInteger(),
                production_unit=JsonString(),
                amount=JsonInteger(),
                means_cost=JsonDecimal(),
                resources_cost=JsonDecimal(),
                labour_cost=JsonDecimal(),
                is_public_service=JsonBoolean(),
                price_per_unit=JsonDecimal(),
                is_cooperating=JsonBoolean(),
                cooperation=JsonString(required=False),
                creation_date=JsonDatetime(),
                approval_date=JsonDatetime(required=False),
                expiration_date=JsonDatetime(required=False),
            ),
            name="PlanDetails",
        )

    def create_view_model(
        self, interactor_response: Optional[GetPlanDetailsInteractor.Response]
    ) -> PlanDetails:
        if not interactor_response:
            raise NotFound("No plan with such ID.")
        return interactor_response.plan_details

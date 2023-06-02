from typing import Optional

from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
    JsonValue,
)
from arbeitszeit_web.api_presenters.response_errors import NotFound


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
                is_available=JsonBoolean(),
                is_cooperating=JsonBoolean(),
                cooperation=JsonString(required=False),
                creation_date=JsonDatetime(),
                approval_date=JsonDatetime(required=False),
                expiration_date=JsonDatetime(required=False),
            ),
            name="PlanSummary",
        )

    def create_view_model(self, plan_summary: Optional[PlanSummary]) -> PlanSummary:
        if not plan_summary:
            raise NotFound("No plan with such ID.")
        return plan_summary

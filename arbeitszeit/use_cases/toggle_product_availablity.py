from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ToggleProductAvailabilityResponse:
    is_success: bool


@dataclass
class ToggleProductAvailability:
    database_gateway: DatabaseGateway

    def __call__(
        self, current_user_id: UUID, plan_id: UUID
    ) -> ToggleProductAvailabilityResponse:
        plan = self.database_gateway.get_plans().with_id(plan_id)
        if not plan:
            return ToggleProductAvailabilityResponse(is_success=False)
        if not plan.planned_by(current_user_id):
            return ToggleProductAvailabilityResponse(is_success=False)
        plan.update().toggle_product_availability().perform()
        return ToggleProductAvailabilityResponse(is_success=True)

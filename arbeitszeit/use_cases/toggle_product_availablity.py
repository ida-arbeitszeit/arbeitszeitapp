from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@dataclass
class ToggleProductAvailabilityResponse:
    is_success: bool


@inject
@dataclass
class ToggleProductAvailability:
    plan_repository: PlanRepository

    def __call__(self, plan_id: UUID) -> ToggleProductAvailabilityResponse:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        if plan is None:
            return ToggleProductAvailabilityResponse(is_success=False)
        self.plan_repository.toggle_product_availability(plan)
        return ToggleProductAvailabilityResponse(is_success=True)

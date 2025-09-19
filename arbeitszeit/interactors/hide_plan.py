from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class HidePlanResponse:
    plan_id: UUID
    is_success: bool


@dataclass
class HidePlanInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self, plan_id: UUID) -> HidePlanResponse:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(plan_id)
        if plan.that_will_expire_after(now):
            return HidePlanResponse(plan_id=plan_id, is_success=False)
        plan.update().hide().perform()
        return HidePlanResponse(plan_id=plan_id, is_success=True)

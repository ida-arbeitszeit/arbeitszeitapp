from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@dataclass
class CancelCooperationSolicitationRequest:
    requester_id: UUID
    plan_id: UUID


@inject
@dataclass
class CancelCooperationSolicitation:
    plan_repo: PlanRepository

    def __call__(self, request: CancelCooperationSolicitationRequest) -> bool:
        plans_changed_count = (
            self.plan_repo.get_plans()
            .with_id(request.plan_id)
            .planned_by(request.requester_id)
            .that_request_cooperation_with_coordinator()
            .update()
            .set_requested_cooperation(None)
            .perform()
        )
        return bool(plans_changed_count)

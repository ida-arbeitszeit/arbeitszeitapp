from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CancelCooperationSolicitationRequest:
    requester_id: UUID
    plan_id: UUID


@dataclass
class CancelCooperationSolicitationInteractor:
    database_gateway: DatabaseGateway

    def execute(self, request: CancelCooperationSolicitationRequest) -> bool:
        plans_changed_count = (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .planned_by(request.requester_id)
            .that_request_cooperation_with_coordinator()
            .update()
            .set_requested_cooperation(None)
            .perform()
        )
        return bool(plans_changed_count)

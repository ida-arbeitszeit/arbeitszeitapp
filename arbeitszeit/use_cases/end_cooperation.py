from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class EndCooperationRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class EndCooperationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        cooperation_not_found = auto()
        plan_has_no_cooperation = auto()
        requester_is_not_authorized = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class EndCooperationUseCase:
    database_gateway: DatabaseGateway

    def execute(self, request: EndCooperationRequest) -> EndCooperationResponse:
        try:
            self._validate_request(request)
        except EndCooperationResponse.RejectionReason as reason:
            return EndCooperationResponse(rejection_reason=reason)
        assert (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .update()
            .set_cooperation(None)
            .perform()
        )
        return EndCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: EndCooperationRequest) -> None:
        plan_and_cooperation = (
            self.database_gateway.get_plans()
            .with_id(request.plan_id)
            .joined_with_cooperation()
            .first()
        )
        cooperation_and_coordinator = (
            self.database_gateway.get_cooperations()
            .with_id(request.cooperation_id)
            .joined_with_current_coordinator()
            .first()
        )
        if not cooperation_and_coordinator:
            raise EndCooperationResponse.RejectionReason.cooperation_not_found
        if plan_and_cooperation is None:
            raise EndCooperationResponse.RejectionReason.plan_not_found
        plan, current_cooperation = plan_and_cooperation
        if not current_cooperation:
            raise EndCooperationResponse.RejectionReason.plan_has_no_cooperation
        coordinator = cooperation_and_coordinator[1]
        if (request.requester_id != coordinator.id) and (
            request.requester_id != plan.planner
        ):
            raise EndCooperationResponse.RejectionReason.requester_is_not_authorized

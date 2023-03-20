from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import CooperationRepository, DatabaseGateway


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
class EndCooperation:
    database_gateway: DatabaseGateway
    cooperation_repository: CooperationRepository

    def __call__(self, request: EndCooperationRequest) -> EndCooperationResponse:
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
        plan = self.database_gateway.get_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise EndCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise EndCooperationResponse.RejectionReason.cooperation_not_found
        if plan.cooperation is None:
            raise EndCooperationResponse.RejectionReason.plan_has_no_cooperation
        if (request.requester_id != cooperation.coordinator.id) and (
            request.requester_id != plan.planner
        ):
            raise EndCooperationResponse.RejectionReason.requester_is_not_authorized

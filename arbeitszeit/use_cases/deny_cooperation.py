from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class DenyCooperationRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class DenyCooperationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        cooperation_not_found = auto()
        cooperation_was_not_requested = auto()
        requester_is_not_coordinator = auto()
        plan_is_inactive = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class DenyCooperationUseCase:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self, request: DenyCooperationRequest) -> DenyCooperationResponse:
        try:
            self._validate_request(request)
        except DenyCooperationResponse.RejectionReason as reason:
            return DenyCooperationResponse(rejection_reason=reason)

        self.database_gateway.get_plans().with_id(
            request.plan_id
        ).update().set_requested_cooperation(None).perform()
        return DenyCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: DenyCooperationRequest) -> None:
        plan = self.database_gateway.get_plans().with_id(request.plan_id).first()
        now = self.datetime_service.now()
        cooperation_and_coordinator = (
            self.database_gateway.get_cooperations()
            .with_id(request.cooperation_id)
            .joined_with_current_coordinator()
            .first()
        )
        if not cooperation_and_coordinator:
            raise DenyCooperationResponse.RejectionReason.cooperation_not_found
        cooperation, coordinator = cooperation_and_coordinator
        if plan is None:
            raise DenyCooperationResponse.RejectionReason.plan_not_found
        if not plan.is_active_as_of(now):
            raise DenyCooperationResponse.RejectionReason.plan_is_inactive
        if plan.requested_cooperation != cooperation.id:
            raise DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
        if request.requester_id != coordinator.id:
            raise DenyCooperationResponse.RejectionReason.requester_is_not_coordinator

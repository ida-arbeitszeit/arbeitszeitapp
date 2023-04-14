from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import CompanyRepository, DatabaseGateway


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

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class DenyCooperation:
    database_gateway: DatabaseGateway
    company_repository: CompanyRepository

    def __call__(self, request: DenyCooperationRequest) -> DenyCooperationResponse:
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
        cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(request.cooperation_id)
            .first()
        )
        if plan is None:
            raise DenyCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise DenyCooperationResponse.RejectionReason.cooperation_not_found
        if plan.requested_cooperation != cooperation.id:
            raise DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
        if request.requester_id != cooperation.coordinator:
            raise DenyCooperationResponse.RejectionReason.requester_is_not_coordinator

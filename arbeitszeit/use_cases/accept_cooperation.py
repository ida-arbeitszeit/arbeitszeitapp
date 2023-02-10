from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanRepository,
)


@dataclass
class AcceptCooperationRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class AcceptCooperationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        cooperation_not_found = auto()
        plan_inactive = auto()
        plan_has_cooperation = auto()
        plan_is_public_service = auto()
        cooperation_was_not_requested = auto()
        requester_is_not_coordinator = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class AcceptCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository

    def __call__(self, request: AcceptCooperationRequest) -> AcceptCooperationResponse:
        try:
            self._validate_request(request)
        except AcceptCooperationResponse.RejectionReason as reason:
            return AcceptCooperationResponse(rejection_reason=reason)
        plan = self.plan_repository.get_plans().with_id(request.plan_id)
        plan.update().set_cooperation(request.cooperation_id).set_requested_cooperation(
            None
        ).perform()
        return AcceptCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: AcceptCooperationRequest) -> None:
        requester = (
            self.company_repository.get_companies()
            .with_id(request.requester_id)
            .first()
        )
        plan = self.plan_repository.get_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise AcceptCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise AcceptCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise AcceptCooperationResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise AcceptCooperationResponse.RejectionReason.plan_has_cooperation
        if plan.is_public_service:
            raise AcceptCooperationResponse.RejectionReason.plan_is_public_service
        if plan.requested_cooperation != cooperation.id:
            raise AcceptCooperationResponse.RejectionReason.cooperation_was_not_requested
        if requester != cooperation.coordinator:
            raise AcceptCooperationResponse.RejectionReason.requester_is_not_coordinator

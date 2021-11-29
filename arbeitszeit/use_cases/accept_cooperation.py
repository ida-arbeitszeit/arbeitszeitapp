from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanCooperationRepository,
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
        plan_already_part_of_cooperation = auto()
        plan_is_public_service = auto()
        cooperation_was_not_requested = auto()
        requester_is_not_coordinator = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class AcceptCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, request: AcceptCooperationRequest) -> AcceptCooperationResponse:
        try:
            self._validate_request(request)
        except AcceptCooperationResponse.RejectionReason as reason:
            return AcceptCooperationResponse(rejection_reason=reason)

        self.plan_cooperation_repository.add_plan_to_cooperation(
            request.plan_id, request.cooperation_id
        )
        self.plan_cooperation_repository.set_requested_cooperation_to_none(
            request.plan_id
        )
        return AcceptCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: AcceptCooperationRequest) -> None:
        requester = self.company_repository.get_by_id(request.requester_id)
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise AcceptCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise AcceptCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise AcceptCooperationResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise AcceptCooperationResponse.RejectionReason.plan_has_cooperation
        if plan in cooperation.plans:
            raise AcceptCooperationResponse.RejectionReason.plan_already_part_of_cooperation
        if plan.is_public_service:
            raise AcceptCooperationResponse.RejectionReason.plan_is_public_service
        if plan.requested_cooperation != cooperation:
            raise AcceptCooperationResponse.RejectionReason.cooperation_was_not_requested
        if requester != cooperation.coordinator:
            raise AcceptCooperationResponse.RejectionReason.requester_is_not_coordinator

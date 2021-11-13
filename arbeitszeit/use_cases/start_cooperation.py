from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanRepository,
)


@dataclass
class StartCooperationRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class StartCooperationResponse:
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
class StartCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository

    def __call__(self, request: StartCooperationRequest) -> StartCooperationResponse:
        try:
            self._validate_request(request)
        except StartCooperationResponse.RejectionReason as reason:
            return StartCooperationResponse(rejection_reason=reason)

        self.cooperation_repository.add_plan_to_cooperation(
            request.plan_id, request.cooperation_id
        )
        self.cooperation_repository.set_requested_cooperation_to_none(request.plan_id)
        return StartCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: StartCooperationRequest) -> None:
        requester = self.company_repository.get_by_id(request.requester_id)
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise StartCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise StartCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise StartCooperationResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise StartCooperationResponse.RejectionReason.plan_has_cooperation
        if plan in cooperation.plans:
            raise StartCooperationResponse.RejectionReason.plan_already_part_of_cooperation
        if plan.is_public_service:
            raise StartCooperationResponse.RejectionReason.plan_is_public_service
        if plan.requested_cooperation != cooperation:
            raise StartCooperationResponse.RejectionReason.cooperation_was_not_requested
        if requester != cooperation.coordinator:
            raise StartCooperationResponse.RejectionReason.requester_is_not_coordinator

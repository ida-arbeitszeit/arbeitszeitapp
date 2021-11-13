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
class AcceptCooperationRequestRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class AcceptCooperationRequestResponse:
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
class AcceptCooperationRequest:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository

    def __call__(
        self, request: AcceptCooperationRequestRequest
    ) -> AcceptCooperationRequestResponse:
        try:
            self._validate_request(request)
        except AcceptCooperationRequestResponse.RejectionReason as reason:
            return AcceptCooperationRequestResponse(rejection_reason=reason)

        self.cooperation_repository.add_plan_to_cooperation(
            request.plan_id, request.cooperation_id
        )
        self.cooperation_repository.set_requested_cooperation_to_none(request.plan_id)
        return AcceptCooperationRequestResponse(rejection_reason=None)

    def _validate_request(self, request: AcceptCooperationRequestRequest) -> None:
        requester = self.company_repository.get_by_id(request.requester_id)
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise AcceptCooperationRequestResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise AcceptCooperationRequestResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise AcceptCooperationRequestResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise AcceptCooperationRequestResponse.RejectionReason.plan_has_cooperation
        if plan in cooperation.plans:
            raise AcceptCooperationRequestResponse.RejectionReason.plan_already_part_of_cooperation
        if plan.is_public_service:
            raise AcceptCooperationRequestResponse.RejectionReason.plan_is_public_service
        if plan.requested_cooperation != cooperation:
            raise AcceptCooperationRequestResponse.RejectionReason.cooperation_was_not_requested
        if requester != cooperation.coordinator:
            raise AcceptCooperationRequestResponse.RejectionReason.requester_is_not_coordinator

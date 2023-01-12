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


@inject
@dataclass
class DenyCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository

    def __call__(self, request: DenyCooperationRequest) -> DenyCooperationResponse:
        try:
            self._validate_request(request)
        except DenyCooperationResponse.RejectionReason as reason:
            return DenyCooperationResponse(rejection_reason=reason)

        self.plan_repository.get_plans().with_id(
            request.plan_id
        ).set_requested_cooperation(None)
        return DenyCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: DenyCooperationRequest) -> None:
        requester = (
            self.company_repository.get_companies()
            .with_id(request.requester_id)
            .first()
        )
        plan = self.plan_repository.get_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise DenyCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise DenyCooperationResponse.RejectionReason.cooperation_not_found
        if plan.requested_cooperation != cooperation.id:
            raise DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
        if requester != cooperation.coordinator:
            raise DenyCooperationResponse.RejectionReason.requester_is_not_coordinator

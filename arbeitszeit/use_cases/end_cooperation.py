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


@inject
@dataclass
class EndCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, request: EndCooperationRequest) -> EndCooperationResponse:
        try:
            self._validate_request(request)
        except EndCooperationResponse.RejectionReason as reason:
            return EndCooperationResponse(rejection_reason=reason)
        self.plan_cooperation_repository.remove_plan_from_cooperation(request.plan_id)
        return EndCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: EndCooperationRequest) -> None:
        requester = self.company_repository.get_by_id(request.requester_id)
        plan = self.plan_repository.get_all_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise EndCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise EndCooperationResponse.RejectionReason.cooperation_not_found
        if plan.cooperation is None:
            raise EndCooperationResponse.RejectionReason.plan_has_no_cooperation
        if (requester != cooperation.coordinator) and (requester != plan.planner):
            raise EndCooperationResponse.RejectionReason.requester_is_not_authorized

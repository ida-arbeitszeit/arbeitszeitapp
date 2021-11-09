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
        plan_not_in_cooperation = auto()
        requester_is_not_entitled = auto()

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

    def __call__(self, request: EndCooperationRequest) -> EndCooperationResponse:
        try:
            self._validate_request(request)
        except EndCooperationResponse.RejectionReason as reason:
            return EndCooperationResponse(rejection_reason=reason)
        self.cooperation_repository.delete_plan_from_cooperation(
            request.plan_id, request.cooperation_id
        )
        self.cooperation_repository.delete_cooperation_from_plan(
            request.plan_id, request.cooperation_id
        )
        return EndCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: EndCooperationRequest) -> None:
        requester = self.company_repository.get_by_id(request.requester_id)
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise EndCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise EndCooperationResponse.RejectionReason.cooperation_not_found
        if plan.cooperation is None:
            raise EndCooperationResponse.RejectionReason.plan_has_no_cooperation
        if plan not in cooperation.plans:
            raise EndCooperationResponse.RejectionReason.plan_not_in_cooperation
        if (requester != cooperation.coordinator) and (requester != plan.planner):
            raise EndCooperationResponse.RejectionReason.requester_is_not_entitled

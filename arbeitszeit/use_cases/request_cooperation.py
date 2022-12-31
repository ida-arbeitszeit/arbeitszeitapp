from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Cooperation
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanCooperationRepository,
    PlanRepository,
)


@dataclass
class RequestCooperationRequest:
    requester_id: UUID
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class RequestCooperationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        cooperation_not_found = auto()
        plan_inactive = auto()
        plan_has_cooperation = auto()
        plan_is_already_requesting_cooperation = auto()
        plan_is_public_service = auto()
        requester_is_not_planner = auto()

    coordinator_name: Optional[str]
    coordinator_email: Optional[str]
    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class RequestCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository
    plan_cooperation_repository: PlanCooperationRepository
    company_repository: CompanyRepository

    def __call__(
        self, request: RequestCooperationRequest
    ) -> RequestCooperationResponse:
        try:
            cooperation = self._validate_request(request)
        except RequestCooperationResponse.RejectionReason as reason:
            return RequestCooperationResponse(
                coordinator_name=None, coordinator_email=None, rejection_reason=reason
            )
        self.plan_cooperation_repository.set_requested_cooperation(
            request.plan_id, request.cooperation_id
        )
        return RequestCooperationResponse(
            coordinator_name=cooperation.coordinator.name,
            coordinator_email=cooperation.coordinator.email,
            rejection_reason=None,
        )

    def _validate_request(self, request: RequestCooperationRequest) -> Cooperation:
        plan = self.plan_repository.get_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise RequestCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise RequestCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise RequestCooperationResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise RequestCooperationResponse.RejectionReason.plan_has_cooperation
        if plan.requested_cooperation:
            raise RequestCooperationResponse.RejectionReason.plan_is_already_requesting_cooperation
        if plan.is_public_service:
            raise RequestCooperationResponse.RejectionReason.plan_is_public_service
        if request.requester_id != plan.planner:
            raise RequestCooperationResponse.RejectionReason.requester_is_not_planner
        return cooperation

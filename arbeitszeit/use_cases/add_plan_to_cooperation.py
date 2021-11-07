from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import CooperationRepository, PlanRepository


@dataclass
class AddPlanToCooperationRequest:
    plan_id: UUID
    cooperation_id: UUID


@dataclass
class AddPlanToCooperationResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        cooperation_not_found = auto()
        plan_inactive = auto()
        plan_has_cooperation = auto()
        plan_already_part_of_cooperation = auto()
        plan_is_public_service = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class AddPlanToCooperation:
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository

    def __call__(
        self, request: AddPlanToCooperationRequest
    ) -> AddPlanToCooperationResponse:
        try:
            self._validate_request(request)
        except AddPlanToCooperationResponse.RejectionReason as reason:
            return AddPlanToCooperationResponse(rejection_reason=reason)

        self.cooperation_repository.add_plan_to_cooperation(
            request.plan_id, request.cooperation_id
        )
        self.cooperation_repository.add_cooperation_to_plan(
            request.plan_id, request.cooperation_id
        )
        return AddPlanToCooperationResponse(rejection_reason=None)

    def _validate_request(self, request: AddPlanToCooperationRequest) -> None:
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise AddPlanToCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise AddPlanToCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active:
            raise AddPlanToCooperationResponse.RejectionReason.plan_inactive
        if plan.cooperation:
            raise AddPlanToCooperationResponse.RejectionReason.plan_has_cooperation
        if plan in cooperation.plans:
            raise AddPlanToCooperationResponse.RejectionReason.plan_already_part_of_cooperation
        if plan.is_public_service:
            raise AddPlanToCooperationResponse.RejectionReason.plan_is_public_service

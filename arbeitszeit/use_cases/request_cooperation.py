from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Cooperation
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    DatabaseGateway,
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


@dataclass
class RequestCooperation:
    database_gateway: DatabaseGateway
    cooperation_repository: CooperationRepository
    company_repository: CompanyRepository
    datetime_service: DatetimeService

    def __call__(
        self, request: RequestCooperationRequest
    ) -> RequestCooperationResponse:
        try:
            cooperation = self._validate_request(request)
        except RequestCooperationResponse.RejectionReason as reason:
            return RequestCooperationResponse(
                coordinator_name=None, coordinator_email=None, rejection_reason=reason
            )
        self.database_gateway.get_plans().with_id(
            request.plan_id
        ).update().set_requested_cooperation(request.cooperation_id).perform()
        return RequestCooperationResponse(
            coordinator_name=cooperation.coordinator.name,
            coordinator_email=cooperation.coordinator.email,
            rejection_reason=None,
        )

    def _validate_request(self, request: RequestCooperationRequest) -> Cooperation:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan_id).first()
        cooperation = self.cooperation_repository.get_by_id(request.cooperation_id)
        if plan is None:
            raise RequestCooperationResponse.RejectionReason.plan_not_found
        if cooperation is None:
            raise RequestCooperationResponse.RejectionReason.cooperation_not_found
        if not plan.is_active_as_of(now):
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

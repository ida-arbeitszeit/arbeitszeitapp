from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Cooperation
from arbeitszeit.repositories import CompanyRepository, DatabaseGateway


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
    company_repository: CompanyRepository
    datetime_service: DatetimeService

    def __call__(
        self, request: RequestCooperationRequest
    ) -> RequestCooperationResponse:
        try:
            _, coordinator = self._validate_request(request)
        except RequestCooperationResponse.RejectionReason as reason:
            return RequestCooperationResponse(
                coordinator_name=None, coordinator_email=None, rejection_reason=reason
            )
        self.database_gateway.get_plans().with_id(
            request.plan_id
        ).update().set_requested_cooperation(request.cooperation_id).perform()
        return RequestCooperationResponse(
            coordinator_name=coordinator.name,
            coordinator_email=coordinator.email,
            rejection_reason=None,
        )

    def _validate_request(
        self, request: RequestCooperationRequest
    ) -> Tuple[Cooperation, Company]:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan_id).first()
        cooperation_and_coordinator = (
            self.database_gateway.get_cooperations()
            .with_id(request.cooperation_id)
            .joined_with_coordinator()
            .first()
        )
        if cooperation_and_coordinator is None:
            raise RequestCooperationResponse.RejectionReason.cooperation_not_found
        if plan is None:
            raise RequestCooperationResponse.RejectionReason.plan_not_found
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
        return cooperation_and_coordinator

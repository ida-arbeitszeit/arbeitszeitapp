from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CreateCooperationRequest:
    coordinator_id: UUID
    name: str
    definition: str


@dataclass
class CreateCooperationResponse:
    class RejectionReason(Exception, Enum):
        coordinator_not_found = auto()
        cooperation_with_name_exists = auto()

    rejection_reason: Optional[RejectionReason]
    cooperation_id: Optional[UUID]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class CreateCooperation:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def __call__(self, request: CreateCooperationRequest) -> CreateCooperationResponse:
        try:
            coordinator = self._validate_request(request)
        except CreateCooperationResponse.RejectionReason as reason:
            return CreateCooperationResponse(
                rejection_reason=reason, cooperation_id=None
            )
        cooperation = self.database_gateway.create_cooperation(
            self.datetime_service.now(),
            request.name,
            request.definition,
        )
        self.database_gateway.create_coordination_tenure(
            company=coordinator.id,
            cooperation=cooperation.id,
            start_date=self.datetime_service.now(),
        )
        return CreateCooperationResponse(
            rejection_reason=None, cooperation_id=cooperation.id
        )

    def _validate_request(self, request: CreateCooperationRequest) -> Company:
        coordinator = (
            self.database_gateway.get_companies()
            .with_id(request.coordinator_id)
            .first()
        )
        coops_with_requested_name = (
            self.database_gateway.get_cooperations().with_name_ignoring_case(
                request.name
            )
        )
        if coordinator is None:
            raise CreateCooperationResponse.RejectionReason.coordinator_not_found
        if coops_with_requested_name:
            raise CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        return coordinator

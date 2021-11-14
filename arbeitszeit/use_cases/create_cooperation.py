from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import CompanyRepository, CooperationRepository


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


@inject
@dataclass
class CreateCooperation:
    company_repository: CompanyRepository
    cooperation_repository: CooperationRepository
    datetime_service: DatetimeService

    def __call__(self, request: CreateCooperationRequest) -> CreateCooperationResponse:
        try:
            self._validate_request(request)
        except CreateCooperationResponse.RejectionReason as reason:
            return CreateCooperationResponse(
                rejection_reason=reason, cooperation_id=None
            )
        coordinator = self.company_repository.get_by_id(request.coordinator_id)
        assert coordinator
        cooperation = self.cooperation_repository.create_cooperation(
            self.datetime_service.now(),
            request.name,
            request.definition,
            coordinator,
        )
        return CreateCooperationResponse(
            rejection_reason=None, cooperation_id=cooperation.id
        )

    def _validate_request(self, request: CreateCooperationRequest) -> None:
        coordinator = self.company_repository.get_by_id(request.coordinator_id)
        coop_with_name_exists = (
            len(list(self.cooperation_repository.get_by_name(request.name))) > 0
        )
        if coordinator is None:
            raise CreateCooperationResponse.RejectionReason.coordinator_not_found
        if coop_with_name_exists:
            raise CreateCooperationResponse.RejectionReason.cooperation_with_name_exists

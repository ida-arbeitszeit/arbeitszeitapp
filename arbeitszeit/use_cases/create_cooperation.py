from dataclasses import dataclass
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
    cooperation_id: UUID


@inject
@dataclass
class CreateCooperation:
    company_repository: CompanyRepository
    cooperation_repository: CooperationRepository
    datetime_service: DatetimeService

    def __call__(
        self, request: CreateCooperationRequest
    ) -> Optional[CreateCooperationResponse]:
        coordinator = self.company_repository.get_by_id(request.coordinator_id)
        if coordinator is None:
            return None
        cooperation = self.cooperation_repository.create_cooperation(
            self.datetime_service.now(),
            request.name,
            request.definition,
            coordinator,
        )
        return CreateCooperationResponse(cooperation_id=cooperation.id)

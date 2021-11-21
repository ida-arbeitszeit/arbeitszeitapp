from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Cooperation
from arbeitszeit.repositories import CompanyRepository, CooperationRepository


@dataclass
class ListCoordinationsRequest:
    company: UUID


@dataclass
class ListCoordinationsResponse:
    coordinations: List[Cooperation]


@inject
@dataclass
class ListCoordinations:
    company_repository: CompanyRepository
    cooperation_repository: CooperationRepository
    datetime_service: DatetimeService

    def __call__(self, request: ListCoordinationsRequest) -> ListCoordinationsResponse:
        if not self.company_repository.get_by_id(request.company):
            return ListCoordinationsResponse(coordinations=[])
        cooperations = list(
            self.cooperation_repository.get_cooperations_coordinated_by_company(
                request.company
            )
        )
        return ListCoordinationsResponse(coordinations=cooperations)

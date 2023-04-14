from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import CompanyRepository, DatabaseGateway


@dataclass
class ListCoordinationsRequest:
    company: UUID


@dataclass
class CooperationInfo:
    id: UUID
    creation_date: datetime
    name: str
    definition: str
    count_plans_in_coop: int


@dataclass
class ListCoordinationsResponse:
    coordinations: List[CooperationInfo]


@dataclass
class ListCoordinations:
    company_repository: CompanyRepository
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def __call__(self, request: ListCoordinationsRequest) -> ListCoordinationsResponse:
        if not self.company_repository.get_companies().with_id(request.company):
            return ListCoordinationsResponse(coordinations=[])
        cooperations = [
            CooperationInfo(
                id=coop.id,
                creation_date=coop.creation_date,
                name=coop.name,
                definition=coop.definition,
                count_plans_in_coop=len(
                    self.database_gateway.get_plans().that_are_part_of_cooperation(
                        coop.id
                    )
                ),
            )
            for coop in self.database_gateway.get_cooperations().coordinated_by_company(
                request.company
            )
        ]

        return ListCoordinationsResponse(coordinations=cooperations)

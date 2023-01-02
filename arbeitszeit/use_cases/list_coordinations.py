from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanRepository,
)


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


@inject
@dataclass
class ListCoordinations:
    company_repository: CompanyRepository
    cooperation_repository: CooperationRepository
    datetime_service: DatetimeService
    plan_repository: PlanRepository

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
                    self.plan_repository.get_plans().that_are_part_of_cooperation(
                        coop.id
                    )
                ),
            )
            for coop in self.cooperation_repository.get_cooperations_coordinated_by_company(
                request.company
            )
        ]

        return ListCoordinationsResponse(coordinations=cooperations)

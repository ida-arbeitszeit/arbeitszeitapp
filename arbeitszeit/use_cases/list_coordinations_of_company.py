from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListCoordinationsOfCompanyRequest:
    company: UUID


@dataclass
class CooperationInfo:
    id: UUID
    creation_date: datetime
    name: str
    definition: str
    count_plans_in_coop: int


@dataclass
class ListCoordinationsOfCompanyResponse:
    coordinations: List[CooperationInfo]


@dataclass
class ListCoordinationsOfCompany:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def __call__(
        self, request: ListCoordinationsOfCompanyRequest
    ) -> ListCoordinationsOfCompanyResponse:
        if not self.database_gateway.get_companies().with_id(request.company):
            return ListCoordinationsOfCompanyResponse(coordinations=[])
        now = self.datetime_service.now()
        cooperations = [
            CooperationInfo(
                id=coop.id,
                creation_date=coop.creation_date,
                name=coop.name,
                definition=coop.definition,
                count_plans_in_coop=len(
                    self.database_gateway.get_plans()
                    .that_are_part_of_cooperation(coop.id)
                    .that_will_expire_after(now)
                ),
            )
            for coop in self.database_gateway.get_cooperations().coordinated_by_company(
                request.company
            )
        ]

        return ListCoordinationsOfCompanyResponse(coordinations=cooperations)

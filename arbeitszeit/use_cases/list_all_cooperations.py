from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Cooperation
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListedCooperation:
    id: UUID
    name: str
    plan_count: int


@dataclass
class ListAllCooperationsResponse:
    cooperations: List[ListedCooperation]


@dataclass
class ListAllCooperationsUseCase:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self) -> ListAllCooperationsResponse:
        all_cooperations = self.database_gateway.get_cooperations()
        if not all_cooperations:
            return ListAllCooperationsResponse(cooperations=[])
        cooperations = [self._coop_to_response_model(coop) for coop in all_cooperations]
        return ListAllCooperationsResponse(cooperations=cooperations)

    def _coop_to_response_model(self, coop: Cooperation) -> ListedCooperation:
        now = self.datetime_service.now()
        plan_count = len(
            self.database_gateway.get_plans()
            .that_are_part_of_cooperation(coop.id)
            .that_will_expire_after(now)
        )
        return ListedCooperation(id=coop.id, name=coop.name, plan_count=plan_count)

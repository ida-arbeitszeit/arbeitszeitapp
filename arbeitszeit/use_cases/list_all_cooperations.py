from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.entities import Cooperation
from arbeitszeit.repositories import CooperationRepository, DatabaseGateway


@dataclass
class ListedCooperation:
    id: UUID
    name: str
    plan_count: int


@dataclass
class ListAllCooperationsResponse:
    cooperations: List[ListedCooperation]


@dataclass
class ListAllCooperations:
    cooperation_repository: CooperationRepository
    database_gateway: DatabaseGateway

    def __call__(self) -> ListAllCooperationsResponse:
        all_cooperations = list(self.cooperation_repository.get_all_cooperations())
        if not all_cooperations:
            return ListAllCooperationsResponse(cooperations=[])
        cooperations = [self._coop_to_response_model(coop) for coop in all_cooperations]
        return ListAllCooperationsResponse(cooperations=cooperations)

    def _coop_to_response_model(self, coop: Cooperation) -> ListedCooperation:
        plan_count = len(
            self.database_gateway.get_plans().that_are_part_of_cooperation(coop.id)
        )
        return ListedCooperation(id=coop.id, name=coop.name, plan_count=plan_count)

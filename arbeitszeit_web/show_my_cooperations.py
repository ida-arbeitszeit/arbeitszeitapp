from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from arbeitszeit.use_cases import (
    ListCooperationRequestsResponse,
    ListCoordinationsResponse,
)


@dataclass
class ListOfCoordinationsRow:
    coop_id: str
    coop_creation_date: str
    coop_name: str
    coop_definition: List[str]
    count_plans_in_coop: str


@dataclass
class ListOfCooperationRequestsRow:
    coop_id: str
    coop_name: str
    plan_id: str
    plan_name: str
    planner_name: str


@dataclass
class ListOfCoordinationsTable:
    rows: List[ListOfCoordinationsRow]


@dataclass
class ListOfCooperationRequestsTable:
    rows: List[ListOfCooperationRequestsRow]


@dataclass
class ShowMyCooperationsViewModel:
    list_of_coordinations: ListOfCoordinationsTable
    list_of_cooperation_requests: ListOfCooperationRequestsTable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCooperationsPresenter:
    def present(
        self,
        list_coop_response: ListCoordinationsResponse,
        list_coop_requests_response: ListCooperationRequestsResponse,
    ) -> ShowMyCooperationsViewModel:
        list_of_coordinations = ListOfCoordinationsTable(
            rows=[
                ListOfCoordinationsRow(
                    coop_id=str(coop.id),
                    coop_creation_date=str(coop.creation_date),
                    coop_name=coop.name,
                    coop_definition=coop.definition.splitlines(),
                    count_plans_in_coop=str(coop.count_plans_in_coop),
                )
                for coop in list_coop_response.coordinations
            ]
        )
        list_of_cooperation_requests = ListOfCooperationRequestsTable(
            rows=[
                ListOfCooperationRequestsRow(
                    coop_id=str(plan.coop_id),
                    coop_name=plan.coop_name,
                    plan_id=str(plan.plan_id),
                    plan_name=plan.plan_name,
                    planner_name=plan.planner_name,
                )
                for plan in list_coop_requests_response.cooperation_requests
            ]
        )
        return ShowMyCooperationsViewModel(
            list_of_coordinations,
            list_of_cooperation_requests,
        )

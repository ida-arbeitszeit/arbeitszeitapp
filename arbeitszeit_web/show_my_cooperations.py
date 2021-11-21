from dataclasses import dataclass, asdict
from arbeitszeit.use_cases import ListCoordinationsResponse
from typing import List, Any, Dict


@dataclass
class ListOfCoordinationsRow:
    coop_id: str
    coop_creation_date: str
    coop_name: str
    coop_definition: List[str]
    count_plans_in_coop: int


@dataclass
class ListOfCoordinationsTable:
    rows: List[ListOfCoordinationsRow]


@dataclass
class ShowMyCooperationsViewModel:
    list_of_coordinations: ListOfCoordinationsTable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCooperationsPresenter:
    def present(
        self, list_coop_response: ListCoordinationsResponse
    ) -> ShowMyCooperationsViewModel:
        list_of_coordinations = ListOfCoordinationsTable(
            rows=[
                ListOfCoordinationsRow(
                    coop_id=str(cooperation.id),
                    coop_creation_date=str(cooperation.creation_date),
                    coop_name=cooperation.name,
                    coop_definition=cooperation.definition.splitlines(),
                    count_plans_in_coop=len(cooperation.plans),
                )
                for cooperation in list_coop_response.coordinations
            ]
        )
        return ShowMyCooperationsViewModel(list_of_coordinations=list_of_coordinations)

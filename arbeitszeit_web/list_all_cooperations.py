from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases import ListAllCooperationsResponse

from .url_index import CoopSummaryUrlIndex


@dataclass
class ListedCooperation:
    id: str
    name: str
    plan_count: str
    coop_summary_url: str


@dataclass
class ListAllCooperationsViewModel:
    cooperations: List[ListedCooperation]
    show_results: bool


@dataclass
class ListAllCooperationsPresenter:
    coop_url_index: CoopSummaryUrlIndex

    def present(
        self, response: ListAllCooperationsResponse
    ) -> ListAllCooperationsViewModel:
        cooperations = [
            ListedCooperation(
                id=str(coop.id),
                name=coop.name,
                plan_count=str(coop.plan_count),
                coop_summary_url=self.coop_url_index.get_coop_summary_url(coop.id),
            )
            for coop in response.cooperations
        ]
        return ListAllCooperationsViewModel(
            cooperations=cooperations, show_results=bool(cooperations)
        )

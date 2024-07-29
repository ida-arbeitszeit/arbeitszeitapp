from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from arbeitszeit.use_cases.list_coordinations_of_company import (
    CooperationInfo,
    ListCoordinationsOfCompanyResponse,
)
from arbeitszeit.use_cases.list_inbound_coop_requests import (
    ListedInboundCoopRequest,
    ListInboundCoopRequestsResponse,
)
from arbeitszeit.use_cases.list_my_cooperating_plans import (
    ListMyCooperatingPlansUseCase,
)
from arbeitszeit.use_cases.list_outbound_coop_requests import (
    ListedOutboundCoopRequest,
    ListOutboundCoopRequestsResponse,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ListOfCoordinationsRow:
    coop_id: str
    coop_creation_date: str
    coop_name: str
    coop_definition: List[str]
    count_plans_in_coop: str
    coop_summary_url: str


@dataclass
class ListOfInboundCooperationRequestsRow:
    coop_id: str
    coop_name: str
    plan_id: str
    plan_name: str
    plan_url: str
    planner_name: str
    planner_url: str


@dataclass
class ListOfOutboundCooperationRequestsRow:
    plan_id: str
    plan_name: str
    plan_url: str
    coop_id: str
    coop_name: str


@dataclass
class CooperatingPlan:
    plan_name: str
    plan_url: str
    coop_name: str
    coop_url: str


@dataclass
class ListOfMyCooperatingPlans:
    rows: List[CooperatingPlan]


@dataclass
class ListOfCoordinationsTable:
    rows: List[ListOfCoordinationsRow]


@dataclass
class ListOfInboundCooperationRequestsTable:
    rows: List[ListOfInboundCooperationRequestsRow]


@dataclass
class ListOfOutboundCooperationRequestsTable:
    rows: List[ListOfOutboundCooperationRequestsRow]


@dataclass
class ShowMyCooperationsViewModel:
    list_of_coordinations: ListOfCoordinationsTable
    list_of_inbound_coop_requests: ListOfInboundCooperationRequestsTable
    list_of_outbound_coop_requests: ListOfOutboundCooperationRequestsTable
    list_of_my_cooperating_plans: ListOfMyCooperatingPlans

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCooperationsPresenter:
    url_index: UrlIndex

    def present(
        self,
        *,
        list_coord_response: ListCoordinationsOfCompanyResponse,
        list_inbound_coop_requests_response: ListInboundCoopRequestsResponse,
        list_outbound_coop_requests_response: ListOutboundCoopRequestsResponse,
        list_my_cooperating_plans_response: ListMyCooperatingPlansUseCase.Response,
    ) -> ShowMyCooperationsViewModel:
        list_of_coordinations = ListOfCoordinationsTable(
            rows=[
                self._display_coordination_table_row(coop)
                for coop in list_coord_response.coordinations
            ]
        )
        list_of_inbound_coop_requests = ListOfInboundCooperationRequestsTable(
            rows=[
                self._display_inbound_coop_requests(plan)
                for plan in list_inbound_coop_requests_response.cooperation_requests
            ]
        )

        list_of_outbound_coop_requests = ListOfOutboundCooperationRequestsTable(
            rows=[
                self._display_outbound_coop_requests(plan)
                for plan in list_outbound_coop_requests_response.cooperation_requests
            ]
        )
        list_of_my_cooperating_plans = ListOfMyCooperatingPlans(
            rows=[
                self._display_my_cooperating_plans(plan)
                for plan in list_my_cooperating_plans_response.cooperating_plans
            ]
        )
        return ShowMyCooperationsViewModel(
            list_of_coordinations,
            list_of_inbound_coop_requests,
            list_of_outbound_coop_requests,
            list_of_my_cooperating_plans,
        )

    def _display_coordination_table_row(
        self, coop: CooperationInfo
    ) -> ListOfCoordinationsRow:
        return ListOfCoordinationsRow(
            coop_id=str(coop.id),
            coop_creation_date=str(coop.creation_date),
            coop_name=coop.name,
            coop_definition=coop.definition.splitlines(),
            count_plans_in_coop=str(coop.count_plans_in_coop),
            coop_summary_url=self.url_index.get_coop_summary_url(coop_id=coop.id),
        )

    def _display_inbound_coop_requests(
        self, plan: ListedInboundCoopRequest
    ) -> ListOfInboundCooperationRequestsRow:
        return ListOfInboundCooperationRequestsRow(
            coop_id=str(plan.coop_id),
            coop_name=plan.coop_name,
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.plan_id
            ),
            planner_name=plan.planner_name,
            planner_url=self.url_index.get_company_summary_url(
                company_id=plan.planner_id
            ),
        )

    def _display_outbound_coop_requests(
        self, plan: ListedOutboundCoopRequest
    ) -> ListOfOutboundCooperationRequestsRow:
        return ListOfOutboundCooperationRequestsRow(
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.plan_id
            ),
            coop_id=str(plan.coop_id),
            coop_name=plan.coop_name,
        )

    def _display_my_cooperating_plans(
        self, plan: ListMyCooperatingPlansUseCase.CooperatingPlan
    ) -> CooperatingPlan:
        return CooperatingPlan(
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.plan_id
            ),
            coop_name=plan.coop_name,
            coop_url=self.url_index.get_coop_summary_url(coop_id=plan.coop_id),
        )

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from arbeitszeit.use_cases import (
    AcceptCooperationResponse,
    ListCoordinationsResponse,
    ListInboundCoopRequestsResponse,
    ListOutboundCoopRequestsResponse,
)

from .url_index import CoopSummaryUrlIndex


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
    planner_name: str


@dataclass
class ListOfOutboundCooperationRequestsRow:
    plan_id: str
    plan_name: str
    coop_id: str
    coop_name: str


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
    accept_message: List[str]
    list_of_outbound_coop_requests: ListOfOutboundCooperationRequestsTable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCooperationsPresenter:
    coop_url_index: CoopSummaryUrlIndex

    def present(
        self,
        list_coord_response: ListCoordinationsResponse,
        list_inbound_coop_requests_response: ListInboundCoopRequestsResponse,
        accept_cooperation_response: Optional[AcceptCooperationResponse],
        list_outbound_coop_requests_response: ListOutboundCoopRequestsResponse,
    ) -> ShowMyCooperationsViewModel:
        list_of_coordinations = ListOfCoordinationsTable(
            rows=[
                ListOfCoordinationsRow(
                    coop_id=str(coop.id),
                    coop_creation_date=str(coop.creation_date),
                    coop_name=coop.name,
                    coop_definition=coop.definition.splitlines(),
                    count_plans_in_coop=str(coop.count_plans_in_coop),
                    coop_summary_url=self.coop_url_index.get_coop_summary_url(coop.id),
                )
                for coop in list_coord_response.coordinations
            ]
        )
        list_of_inbound_coop_requests = ListOfInboundCooperationRequestsTable(
            rows=[
                ListOfInboundCooperationRequestsRow(
                    coop_id=str(plan.coop_id),
                    coop_name=plan.coop_name,
                    plan_id=str(plan.plan_id),
                    plan_name=plan.plan_name,
                    planner_name=plan.planner_name,
                )
                for plan in list_inbound_coop_requests_response.cooperation_requests
            ]
        )

        accept_message = (
            self._create_accept_message(accept_cooperation_response)
            if accept_cooperation_response
            else []
        )

        list_of_outbound_coop_requests = ListOfOutboundCooperationRequestsTable(
            rows=[
                ListOfOutboundCooperationRequestsRow(
                    plan_id=str(plan.plan_id),
                    plan_name=plan.plan_name,
                    coop_id=str(plan.coop_id),
                    coop_name=plan.coop_name,
                )
                for plan in list_outbound_coop_requests_response.cooperation_requests
            ]
        )

        return ShowMyCooperationsViewModel(
            list_of_coordinations,
            list_of_inbound_coop_requests,
            accept_message,
            list_of_outbound_coop_requests,
        )

    def _create_accept_message(
        self, accept_cooperation_response: AcceptCooperationResponse
    ) -> List[str]:
        if not accept_cooperation_response.is_rejected:
            accept_message = ["Kooperationsanfrage wurde angenommen."]
        else:
            if (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.plan_not_found
                or AcceptCooperationResponse.RejectionReason.cooperation_not_found
            ):
                accept_message = ["Plan oder Kooperation nicht gefunden."]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.plan_inactive
                or AcceptCooperationResponse.RejectionReason.plan_has_cooperation
                or AcceptCooperationResponse.RejectionReason.plan_is_public_service
            ):
                accept_message = ["Mit dem Plan stimmt etwas nicht."]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                accept_message = ["Diese Kooperationsanfrage existiert nicht."]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                accept_message = ["Du bist nicht Koordinator dieser Kooperation."]
        return accept_message

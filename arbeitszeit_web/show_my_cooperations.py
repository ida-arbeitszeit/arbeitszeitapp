from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from arbeitszeit.use_cases import (
    AcceptCooperationResponse,
    CooperationInfo,
    DenyCooperationResponse,
    ListCoordinationsResponse,
    ListedInboundCoopRequest,
    ListedOutboundCoopRequest,
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
    accept_message_success: bool
    deny_message: List[str]
    deny_message_success: bool
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
        deny_cooperation_response: Optional[DenyCooperationResponse],
        list_outbound_coop_requests_response: ListOutboundCoopRequestsResponse,
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

        accept_message, accept_message_success = self._accept_message_info(
            accept_cooperation_response
        )

        deny_message, deny_message_success = self._deny_message_info(
            deny_cooperation_response
        )

        list_of_outbound_coop_requests = ListOfOutboundCooperationRequestsTable(
            rows=[
                self._display_outbound_coop_requests(plan)
                for plan in list_outbound_coop_requests_response.cooperation_requests
            ]
        )

        return ShowMyCooperationsViewModel(
            list_of_coordinations,
            list_of_inbound_coop_requests,
            accept_message,
            accept_message_success,
            deny_message,
            deny_message_success,
            list_of_outbound_coop_requests,
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
            coop_summary_url=self.coop_url_index.get_coop_summary_url(coop.id),
        )

    def _display_inbound_coop_requests(
        self, plan: ListedInboundCoopRequest
    ) -> ListOfInboundCooperationRequestsRow:
        return ListOfInboundCooperationRequestsRow(
            coop_id=str(plan.coop_id),
            coop_name=plan.coop_name,
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            planner_name=plan.planner_name,
        )

    def _display_outbound_coop_requests(
        self, plan: ListedOutboundCoopRequest
    ) -> ListOfOutboundCooperationRequestsRow:
        return ListOfOutboundCooperationRequestsRow(
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            coop_id=str(plan.coop_id),
            coop_name=plan.coop_name,
        )

    def _accept_message_info(
        self, accept_cooperation_response: Optional[AcceptCooperationResponse]
    ) -> Tuple[List[str], bool]:

        if accept_cooperation_response:
            accept_message, accept_message_success = self._create_accept_message(
                accept_cooperation_response
            )
        else:
            accept_message, accept_message_success = [], False
        return accept_message, accept_message_success

    def _create_accept_message(
        self, accept_cooperation_response: AcceptCooperationResponse
    ) -> Tuple[List[str], bool]:
        if not accept_cooperation_response.is_rejected:
            accept_message = ["Kooperationsanfrage wurde angenommen."]
            accept_message_success = True
        else:
            accept_message_success = False
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
        return accept_message, accept_message_success

    def _deny_message_info(
        self, deny_cooperation_response: Optional[DenyCooperationResponse]
    ) -> Tuple[List[str], bool]:

        if deny_cooperation_response:
            deny_message, deny_message_success = self._create_deny_message(
                deny_cooperation_response
            )
        else:
            deny_message, deny_message_success = [], False
        return deny_message, deny_message_success

    def _create_deny_message(
        self, deny_cooperation_response: DenyCooperationResponse
    ) -> Tuple[List[str], bool]:
        if not deny_cooperation_response.is_rejected:
            deny_message = ["Kooperationsanfrage wurde abgelehnt."]
            deny_message_success = True
        else:
            deny_message_success = False
            if (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.plan_not_found
                or DenyCooperationResponse.RejectionReason.cooperation_not_found
            ):
                deny_message = ["Plan oder Kooperation nicht gefunden."]
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                deny_message = ["Diese Kooperationsanfrage existiert nicht."]
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                deny_message = ["Du bist nicht Koordinator dieser Kooperation."]
        return deny_message, deny_message_success

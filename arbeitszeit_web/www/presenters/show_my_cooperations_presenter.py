from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from arbeitszeit.use_cases.accept_cooperation import AcceptCooperationResponse
from arbeitszeit.use_cases.deny_cooperation import DenyCooperationResponse
from arbeitszeit.use_cases.list_coordinations import (
    CooperationInfo,
    ListCoordinationsResponse,
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
from arbeitszeit_web.translator import Translator
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
    accept_message: List[str]
    accept_message_success: bool
    deny_message: List[str]
    deny_message_success: bool
    list_of_outbound_coop_requests: ListOfOutboundCooperationRequestsTable
    list_of_my_cooperating_plans: ListOfMyCooperatingPlans
    cancel_message: List[str]
    cancel_message_success: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyCooperationsPresenter:
    url_index: UrlIndex
    translator: Translator

    def present(
        self,
        list_coord_response: ListCoordinationsResponse,
        list_inbound_coop_requests_response: ListInboundCoopRequestsResponse,
        accept_cooperation_response: Optional[AcceptCooperationResponse],
        deny_cooperation_response: Optional[DenyCooperationResponse],
        list_outbound_coop_requests_response: ListOutboundCoopRequestsResponse,
        cancel_cooperation_solicitation_response: Optional[bool],
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

        accept_message, accept_message_success = self._accept_message_info(
            accept_cooperation_response
        )

        deny_message, deny_message_success = self._deny_message_info(
            deny_cooperation_response
        )

        cancel_message, cancel_message_success = self._cancel_message_info(
            cancel_cooperation_solicitation_response
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
            accept_message,
            accept_message_success,
            deny_message,
            deny_message_success,
            list_of_outbound_coop_requests,
            list_of_my_cooperating_plans,
            cancel_message,
            cancel_message_success,
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
            coop_summary_url=self.url_index.get_coop_summary_url(
                user_role=UserRole.company, coop_id=coop.id
            ),
        )

    def _display_inbound_coop_requests(
        self, plan: ListedInboundCoopRequest
    ) -> ListOfInboundCooperationRequestsRow:
        return ListOfInboundCooperationRequestsRow(
            coop_id=str(plan.coop_id),
            coop_name=plan.coop_name,
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_summary_url(
                user_role=UserRole.company, plan_id=plan.plan_id
            ),
            planner_name=plan.planner_name,
            planner_url=self.url_index.get_company_summary_url(
                user_role=UserRole.company, company_id=plan.planner_id
            ),
        )

    def _display_outbound_coop_requests(
        self, plan: ListedOutboundCoopRequest
    ) -> ListOfOutboundCooperationRequestsRow:
        return ListOfOutboundCooperationRequestsRow(
            plan_id=str(plan.plan_id),
            plan_name=plan.plan_name,
            plan_url=self.url_index.get_plan_summary_url(
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
            plan_url=self.url_index.get_plan_summary_url(
                user_role=UserRole.company, plan_id=plan.plan_id
            ),
            coop_name=plan.coop_name,
            coop_url=self.url_index.get_coop_summary_url(
                user_role=UserRole.company, coop_id=plan.coop_id
            ),
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
            accept_message = [
                self.translator.gettext("Cooperation request has been accepted.")
            ]
            accept_message_success = True
        else:
            accept_message_success = False
            if (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.plan_not_found
                or AcceptCooperationResponse.RejectionReason.cooperation_not_found
            ):
                accept_message = [
                    self.translator.gettext("Plan or cooperation not found.")
                ]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.plan_inactive
                or AcceptCooperationResponse.RejectionReason.plan_has_cooperation
                or AcceptCooperationResponse.RejectionReason.plan_is_public_service
            ):
                accept_message = [
                    self.translator.gettext("Something's wrong with that plan.")
                ]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                accept_message = [
                    self.translator.gettext("This cooperation request does not exist.")
                ]
            elif (
                accept_cooperation_response
                == AcceptCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                accept_message = [
                    self.translator.gettext(
                        "You are not coordinator of this cooperation."
                    )
                ]
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
            deny_message = [
                self.translator.gettext("Cooperation request has been denied.")
            ]
            deny_message_success = True
        else:
            deny_message_success = False
            if (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.plan_not_found
                or DenyCooperationResponse.RejectionReason.cooperation_not_found
            ):
                deny_message = [
                    self.translator.gettext("Plan or cooperation not found.")
                ]
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                deny_message = [
                    self.translator.gettext("This cooperation request does not exist.")
                ]
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                deny_message = [
                    self.translator.gettext(
                        "You are not coordinator of this cooperation."
                    )
                ]
            else:
                # catchall for rejected responses where rejection
                # reason cannot be handled by presenter.
                deny_message = [self.translator.gettext("Could not deny cooperation")]
        return deny_message, deny_message_success

    def _cancel_message_info(
        self, cancel_coop_response: Optional[bool]
    ) -> Tuple[List[str], bool]:
        if cancel_coop_response is None:
            return [], False
        elif cancel_coop_response == True:
            return [
                self.translator.gettext("Cooperation request has been canceled.")
            ], True
        else:
            return [
                self.translator.gettext("Error: Not possible to cancel request.")
            ], False

from datetime import datetime
from unittest import TestCase
from uuid import uuid4

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
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl

LIST_COORDINATIONS_RESPONSE_LEN_1 = ListCoordinationsResponse(
    coordinations=[
        CooperationInfo(
            id=uuid4(),
            creation_date=datetime.now(),
            name="coop name",
            definition="first paragraph\nsecond paragraph",
            count_plans_in_coop=3,
        )
    ]
)

LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1 = ListInboundCoopRequestsResponse(
    cooperation_requests=[
        ListedInboundCoopRequest(
            coop_id=uuid4(),
            coop_name="coop name",
            plan_id=uuid4(),
            plan_name="plan name",
            planner_name="planner name",
        )
    ]
)

LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1 = ListOutboundCoopRequestsResponse(
    cooperation_requests=[
        ListedOutboundCoopRequest(
            plan_id=uuid4(),
            plan_name="plan name",
            coop_id=uuid4(),
            coop_name="coop name",
        )
    ]
)


class ShowMyCooperationsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = FakeTranslator()
        self.presenter = self.injector.get(ShowMyCooperationsPresenter)

    def test_coordinations_are_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
            DenyCooperationResponse(rejection_reason=None),
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertEqual(len(presentation.list_of_coordinations.rows), 1)
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_id,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id),
        )
        coop_id = LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_summary_url,
            self.url_index.get_coop_summary_url(
                coop_id=coop_id, user_role=UserRole.company
            ),
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_creation_date,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].creation_date),
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_name,
            LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].name,
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_definition,
            ["first paragraph", "second paragraph"],
        )
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].count_plans_in_coop,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].count_plans_in_coop),
        )

    def test_inbound_cooperation_requests_are_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
            DenyCooperationResponse(rejection_reason=None),
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertEqual(len(presentation.list_of_inbound_coop_requests.rows), 1)
        self.assertEqual(
            presentation.list_of_inbound_coop_requests.rows[0].coop_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_name,
        )
        self.assertEqual(
            presentation.list_of_inbound_coop_requests.rows[0].coop_id,
            str(LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_id),
        )
        self.assertEqual(
            presentation.list_of_inbound_coop_requests.rows[0].plan_id,
            str(LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_id),
        )
        self.assertEqual(
            presentation.list_of_inbound_coop_requests.rows[0].plan_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_name,
        )
        self.assertEqual(
            presentation.list_of_inbound_coop_requests.rows[0].planner_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].planner_name,
        )

    def test_successfull_accept_request_response_is_presented_correctly(self):
        presentation_success = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
            None,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertTrue(presentation_success.accept_message_success)
        self.assertFalse(presentation_success.deny_message_success)
        self.assertEqual(
            len(presentation_success.accept_message),
            1,
        )
        self.assertEqual(
            presentation_success.accept_message[0],
            self.translator.gettext("Cooperation request has been accepted."),
        )

    def test_successfull_deny_request_response_is_presented_correctly(self):
        presentation_success = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
            DenyCooperationResponse(rejection_reason=None),
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertTrue(presentation_success.deny_message_success)
        self.assertFalse(presentation_success.accept_message_success)
        self.assertEqual(
            len(presentation_success.deny_message),
            1,
        )
        self.assertEqual(
            presentation_success.deny_message[0],
            self.translator.gettext("Cooperation request has been denied."),
        )

    def test_failed_accept_request_response_is_presented_correctly(self):
        presentation_failure = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(
                rejection_reason=AcceptCooperationResponse.RejectionReason.plan_not_found
            ),
            None,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertFalse(presentation_failure.accept_message_success)
        self.assertFalse(presentation_failure.deny_message_success)
        self.assertEqual(
            len(presentation_failure.accept_message),
            1,
        )
        self.assertEqual(
            presentation_failure.accept_message[0],
            self.translator.gettext("Plan or cooperation not found."),
        )

    def test_failed_deny_request_response_is_presented_correctly(self):
        presentation_failure = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
            DenyCooperationResponse(
                rejection_reason=DenyCooperationResponse.RejectionReason.plan_not_found
            ),
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertFalse(presentation_failure.deny_message_success)
        self.assertFalse(presentation_failure.accept_message_success)
        self.assertEqual(
            len(presentation_failure.deny_message),
            1,
        )
        self.assertEqual(
            presentation_failure.deny_message[0],
            self.translator.gettext("Plan or cooperation not found."),
        )

    def test_outbound_cooperation_requests_are_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
            DenyCooperationResponse(rejection_reason=None),
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
        )
        self.assertEqual(len(presentation.list_of_outbound_coop_requests.rows), 1)
        self.assertEqual(
            presentation.list_of_outbound_coop_requests.rows[0].plan_id,
            str(
                LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_id
            ),
        )
        self.assertEqual(
            presentation.list_of_outbound_coop_requests.rows[0].plan_name,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_name,
        )
        self.assertEqual(
            presentation.list_of_outbound_coop_requests.rows[0].coop_name,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_name,
        )
        self.assertEqual(
            presentation.list_of_outbound_coop_requests.rows[0].coop_id,
            str(
                LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_id
            ),
        )

    def test_successfull_cancel_request_response_is_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
            None,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            True,
        )
        self.assertTrue(presentation.cancel_message_success)
        self.assertEqual(
            len(presentation.cancel_message),
            1,
        )
        self.assertEqual(
            presentation.cancel_message[0],
            self.translator.gettext("Cooperation request has been canceled."),
        )

    def test_failed_cancel_request_response_is_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            None,
            None,
            LIST_OUTBD_COOP_REQUESTS_RESPONSE_LEN_1,
            False,
        )
        self.assertFalse(presentation.cancel_message_success)
        self.assertEqual(
            len(presentation.cancel_message),
            1,
        )
        self.assertEqual(
            presentation.cancel_message[0],
            self.translator.gettext("Error: Not possible to cancel request."),
        )

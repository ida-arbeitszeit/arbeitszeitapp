from unittest import TestCase

from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from arbeitszeit.use_cases import (
    ListCoordinationsResponse,
    ListInboundCoopRequestsResponse,
    AcceptCooperationResponse,
    CooperationInfo,
    ListedCoopRequest,
)
from uuid import uuid4
from datetime import datetime

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
        ListedCoopRequest(
            coop_id=uuid4(),
            coop_name="coop name",
            plan_id=uuid4(),
            plan_name="plan name",
            planner_name="planner name",
        )
    ]
)


class ShowMyCooperationsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = ShowMyCooperationsPresenter()

    def test_coordinations_are_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
        )
        self.assertEqual(len(presentation.list_of_coordinations.rows), 1)
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_id,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id),
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

    def test_cooperation_requests_are_presented_correctly(self):
        presentation = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
        )
        self.assertEqual(len(presentation.list_of_cooperation_requests.rows), 1)
        self.assertEqual(
            presentation.list_of_cooperation_requests.rows[0].coop_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_name,
        )
        self.assertEqual(
            presentation.list_of_cooperation_requests.rows[0].coop_id,
            str(LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].coop_id),
        )
        self.assertEqual(
            presentation.list_of_cooperation_requests.rows[0].plan_id,
            str(LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_id),
        )
        self.assertEqual(
            presentation.list_of_cooperation_requests.rows[0].plan_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].plan_name,
        )
        self.assertEqual(
            presentation.list_of_cooperation_requests.rows[0].planner_name,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1.cooperation_requests[0].planner_name,
        )

    def test_successfull_accept_request_response_is_presented_correctly(self):
        presentation_success = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(rejection_reason=None),
        )
        self.assertEqual(
            len(presentation_success.accept_message),
            1,
        )
        self.assertEqual(
            presentation_success.accept_message[0],
            "Kooperationsanfrage wurde angenommen.",
        )

    def test_failed_accept_request_response_is_presented_correctly(self):
        presentation_failure = self.presenter.present(
            LIST_COORDINATIONS_RESPONSE_LEN_1,
            LIST_INBD_COOP_REQUESTS_RESPONSE_LEN_1,
            AcceptCooperationResponse(
                rejection_reason=AcceptCooperationResponse.RejectionReason.plan_not_found
            ),
        )
        self.assertEqual(
            len(presentation_failure.accept_message),
            1,
        )
        self.assertEqual(
            presentation_failure.accept_message[0],
            "Plan oder Kooperation nicht gefunden.",
        )

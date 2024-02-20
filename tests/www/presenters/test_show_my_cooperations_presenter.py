from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.accept_cooperation import AcceptCooperationResponse
from arbeitszeit.use_cases.deny_cooperation import DenyCooperationResponse
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
from arbeitszeit_web.www.presenters.show_my_cooperations_presenter import (
    ShowMyCooperationsPresenter,
)
from tests.www.base_test_case import BaseTestCase

LIST_COORDINATIONS_RESPONSE_LEN_1 = ListCoordinationsOfCompanyResponse(
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


def get_inbound_response_length_1(
    coop_id: Optional[UUID] = None,
    plan_id: Optional[UUID] = None,
    planner_id: Optional[UUID] = None,
) -> ListInboundCoopRequestsResponse:
    if coop_id is None:
        coop_id = uuid4()
    if plan_id is None:
        plan_id = uuid4()
    if planner_id is None:
        planner_id = uuid4()
    return ListInboundCoopRequestsResponse(
        cooperation_requests=[
            ListedInboundCoopRequest(
                coop_id=coop_id,
                coop_name="coop name",
                plan_id=plan_id,
                plan_name="plan name",
                planner_name="planner name",
                planner_id=planner_id,
            )
        ]
    )


def get_outbound_response_length_1(
    plan_id: Optional[UUID] = None, coop_id: Optional[UUID] = None
) -> ListOutboundCoopRequestsResponse:
    if plan_id is None:
        plan_id = uuid4()
    if coop_id is None:
        coop_id = uuid4()
    return ListOutboundCoopRequestsResponse(
        cooperation_requests=[
            ListedOutboundCoopRequest(
                plan_id=plan_id,
                plan_name="plan name",
                coop_id=coop_id,
                coop_name="coop name",
            )
        ]
    )


def get_coop_plans_response_length_1(
    plan_id: Optional[UUID] = None, coop_id: Optional[UUID] = None
) -> ListMyCooperatingPlansUseCase.Response:
    if plan_id is None:
        plan_id = uuid4()
    if coop_id is None:
        coop_id = uuid4()
    return ListMyCooperatingPlansUseCase.Response(
        cooperating_plans=[
            ListMyCooperatingPlansUseCase.CooperatingPlan(
                plan_id=plan_id,
                plan_name="test plan name",
                coop_id=coop_id,
                coop_name="test coop name",
            )
        ]
    )


class ShowMyCooperationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCooperationsPresenter)

    def test_coordinations_are_presented_correctly(self) -> None:
        presentation = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )
        self.assertEqual(len(presentation.list_of_coordinations.rows), 1)
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_id,
            str(LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id),
        )
        coop_id = LIST_COORDINATIONS_RESPONSE_LEN_1.coordinations[0].id
        self.assertEqual(
            presentation.list_of_coordinations.rows[0].coop_summary_url,
            self.url_index.get_coop_summary_url(coop_id=coop_id),
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

    def test_successfull_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
            accept_cooperation_response=AcceptCooperationResponse(
                rejection_reason=None
            ),
        )
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been accepted."
        )
        assert not self.notifier.warnings

    def test_successfull_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            deny_cooperation_response=DenyCooperationResponse(rejection_reason=None),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been denied."
        )

    def test_failed_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
            accept_cooperation_response=AcceptCooperationResponse(
                rejection_reason=AcceptCooperationResponse.RejectionReason.plan_not_found
            ),
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan or cooperation not found."
        )

    def test_failed_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            deny_cooperation_response=DenyCooperationResponse(
                rejection_reason=DenyCooperationResponse.RejectionReason.plan_not_found
            ),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan or cooperation not found."
        )

    def test_successfull_cancel_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            cancel_cooperation_solicitation_response=True,
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been canceled."
        )

    def test_failed_cancel_request_response_is_presented_correctly(self) -> None:
        self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            cancel_cooperation_solicitation_response=False,
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Error: Not possible to cancel request."
        )


class InboundTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCooperationsPresenter)
        self.COOP_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.PLANNER_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(
                coop_id=self.COOP_ID, plan_id=self.PLAN_ID, planner_id=self.PLANNER_ID
            ),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )

    def test_inbound_coop_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_coop_requests.rows[0].coop_name,
        )

    def test_inbound_plan_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_coop_requests.rows[0].plan_name,
        )

    def test_inbound_planner_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_inbound_coop_requests.rows[0].planner_name,
        )

    def test_inbound_coop_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_coop_requests.rows[0].coop_id,
            str(self.COOP_ID),
        )

    def test_inbound_plan_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_coop_requests.rows[0].plan_id,
            str(self.PLAN_ID),
        )

    def test_inbound_plan_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_coop_requests.rows[0].plan_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=self.PLAN_ID
            ),
        )

    def test_inbound_planner_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_inbound_coop_requests.rows[0].planner_url,
            self.url_index.get_company_summary_url(company_id=self.PLANNER_ID),
        )


class OutboundTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCooperationsPresenter)
        self.COOP_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            list_outbound_coop_requests_response=get_outbound_response_length_1(
                plan_id=self.PLAN_ID, coop_id=self.COOP_ID
            ),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(),
        )

    def test_outbound_plan_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_coop_requests.rows[0].plan_id,
            str(self.PLAN_ID),
        )

    def test_outbound_coop_id_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_coop_requests.rows[0].coop_id,
            str(self.COOP_ID),
        )

    def test_outbound_coop_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_outbound_coop_requests.rows[0].coop_name,
        )

    def test_outbound_plan_name_is_presented(self) -> None:
        self.assertTrue(
            self.view_model.list_of_outbound_coop_requests.rows[0].plan_name,
        )

    def test_outbound_plan_url_is_presented_correctly(self) -> None:
        self.assertEqual(
            self.view_model.list_of_outbound_coop_requests.rows[0].plan_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=self.PLAN_ID
            ),
        )


class CooperatingPlansTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyCooperationsPresenter)
        self.COOP_ID = uuid4()
        self.PLAN_ID = uuid4()
        self.view_model = self.presenter.present(
            list_coord_response=LIST_COORDINATIONS_RESPONSE_LEN_1,
            list_inbound_coop_requests_response=get_inbound_response_length_1(),
            accept_cooperation_response=AcceptCooperationResponse(
                rejection_reason=None
            ),
            list_outbound_coop_requests_response=get_outbound_response_length_1(),
            list_my_cooperating_plans_response=get_coop_plans_response_length_1(
                plan_id=self.PLAN_ID, coop_id=self.COOP_ID
            ),
        )

    def test_show_one_plan_if_one_plan_exists(self) -> None:
        assert len(self.view_model.list_of_my_cooperating_plans.rows) == 1

    def test_name_of_plan_is_shown(self) -> None:
        assert self.view_model.list_of_my_cooperating_plans.rows[0].plan_name

    def test_name_of_cooperation_is_shown(self) -> None:
        assert self.view_model.list_of_my_cooperating_plans.rows[0].coop_name

    def test_plan_url_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=self.PLAN_ID
            ),
            self.view_model.list_of_my_cooperating_plans.rows[0].plan_url,
        )

    def test_coop_url_is_shown_correctly(self) -> None:
        self.assertEqual(
            self.url_index.get_coop_summary_url(coop_id=self.COOP_ID),
            self.view_model.list_of_my_cooperating_plans.rows[0].coop_url,
        )

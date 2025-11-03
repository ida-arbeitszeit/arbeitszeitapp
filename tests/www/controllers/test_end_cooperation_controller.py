from uuid import UUID, uuid4

from arbeitszeit.interactors.end_cooperation import EndCooperationRequest
from arbeitszeit_web.www.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class EndCooperationControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(EndCooperationController)

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("cooperation_id", str(uuid4()))
        self.session.logout()
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_no_plan_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", "")
        request.set_form("cooperation_id", str(uuid4()))
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_a_malformed_plan_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", "jsbbjs8sjns")
        request.set_form("cooperation_id", str(uuid4()))
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_no_cooperation_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("cooperation_id", "")
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_when_request_has_malformed_cooperation_id_then_we_cannot_get_a_interactor_request(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("cooperation_id", "jnsjsn8snks")
        self.session.login_company(uuid4())
        self.assertIsNone(self.controller.process_request_data(request))

    def test_a_interactor_request_can_get_returned(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("plan_id", str(uuid4()))
        request.set_form("cooperation_id", str(uuid4()))
        self.session.login_company(uuid4())
        interactor_request = self.controller.process_request_data(request)
        self.assertIsNotNone(interactor_request)
        self.assertIsInstance(interactor_request, EndCooperationRequest)

    def test_a_interactor_request_with_correct_attributes_gets_returned(
        self,
    ) -> None:
        request = FakeRequest()
        plan_id = str(uuid4())
        cooperation_id = str(uuid4())
        user_id = uuid4()
        request.set_form("plan_id", plan_id)
        request.set_form("cooperation_id", cooperation_id)
        self.session.login_company(user_id)
        interactor_request = self.controller.process_request_data(request)
        assert interactor_request
        self.assertEqual(interactor_request.plan_id, UUID(plan_id))
        self.assertEqual(interactor_request.cooperation_id, UUID(cooperation_id))
        self.assertEqual(interactor_request.requester_id, user_id)

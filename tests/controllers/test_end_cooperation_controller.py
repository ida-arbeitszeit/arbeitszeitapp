from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.end_cooperation import EndCooperationRequest
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from tests.flask_integration.request import FakeRequest
from tests.session import FakeSession


class EndCooperationControllerTests(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.request = FakeRequest()
        self.controller = EndCooperationController(
            session=self.session, request=self.request
        )

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.request.set_arg("plan_id", str(uuid4()))
        self.request.set_arg("cooperation_id", str(uuid4()))
        self.session.set_current_user_id(None)
        self.assertIsNone(self.controller.process_request_data())

    def test_when_request_has_no_plan_id_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.request.set_arg("plan_id", "")
        self.request.set_arg("cooperation_id", str(uuid4()))
        self.session.set_current_user_id(uuid4())
        self.assertIsNone(self.controller.process_request_data())

    def test_when_request_has_a_malformed_plan_id_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.request.set_arg("plan_id", "jsbbjs8sjns")
        self.request.set_arg("cooperation_id", str(uuid4()))
        self.session.set_current_user_id(uuid4())
        self.assertIsNone(self.controller.process_request_data())

    def test_when_request_has_no_cooperation_id_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.request.set_arg("plan_id", str(uuid4()))
        self.request.set_arg("cooperation_id", "")
        self.session.set_current_user_id(uuid4())
        self.assertIsNone(self.controller.process_request_data())

    def test_when_request_has_malformed_cooperation_id_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.request.set_arg("plan_id", str(uuid4()))
        self.request.set_arg("cooperation_id", "jnsjsn8snks")
        self.session.set_current_user_id(uuid4())
        self.assertIsNone(self.controller.process_request_data())

    def test_a_use_case_request_can_get_returned(
        self,
    ) -> None:
        self.request.set_arg("plan_id", str(uuid4()))
        self.request.set_arg("cooperation_id", str(uuid4()))
        self.session.set_current_user_id(uuid4())
        use_case_request = self.controller.process_request_data()
        self.assertIsNotNone(use_case_request)
        self.assertIsInstance(use_case_request, EndCooperationRequest)

    def test_a_use_case_request_with_correct_attributes_gets_returned(
        self,
    ) -> None:
        plan_id = str(uuid4())
        cooperation_id = str(uuid4())
        user_id = uuid4()
        self.request.set_arg("plan_id", plan_id)
        self.request.set_arg("cooperation_id", cooperation_id)
        self.session.set_current_user_id(user_id)
        use_case_request = self.controller.process_request_data()
        assert use_case_request
        self.assertEqual(use_case_request.plan_id, UUID(plan_id))
        self.assertEqual(use_case_request.cooperation_id, UUID(cooperation_id))
        self.assertEqual(use_case_request.requester_id, user_id)

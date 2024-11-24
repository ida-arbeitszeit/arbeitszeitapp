from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases.register_hours_worked import RegisterHoursWorkedRequest
from arbeitszeit_web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
    RegisterHoursWorkedController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class RegisterHoursWorkedControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterHoursWorkedController)

    def test_when_company_is_not_authenticated_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", str(uuid4()))
        request.set_form("amount", "10")
        self.session.logout()
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_no_member_id_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", "")
        request.set_form("amount", "10")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_malformed_member_id_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", "invalid_id")
        request.set_form("amount", "10")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_no_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", str(uuid4()))
        request.set_form("amount", "")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_malformed_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", str(uuid4()))
        request.set_form("amount", "abc")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_negative_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", str(uuid4()))
        request.set_form("amount", "-1")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.negative_amount,
        )

    def test_a_use_case_request_can_get_returned(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_form("member_id", str(uuid4()))
        request.set_form("amount", "10")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        self.assertIsInstance(controller_response, RegisterHoursWorkedRequest)

    def test_a_use_case_request_with_correct_attributes_can_get_returned(
        self,
    ) -> None:
        request = FakeRequest()
        member_id = uuid4()
        request.set_form("member_id", str(member_id))
        request.set_form("amount", "10")
        user_id = uuid4()
        self.session.login_company(user_id)
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, RegisterHoursWorkedRequest)
        self.assertEqual(controller_response.company_id, user_id)
        self.assertEqual(controller_response.worker_id, member_id)
        self.assertEqual(controller_response.hours_worked, Decimal("10"))

    def test_worker_uuid_gets_stripped(
        self,
    ) -> None:
        request = FakeRequest()
        member_id = uuid4()
        request.set_form("member_id", " " + str(member_id) + " ")
        request.set_form("amount", "10")
        self.session.login_company(uuid4())
        controller_response = self.controller.create_use_case_request(request)
        assert isinstance(controller_response, RegisterHoursWorkedRequest)
        self.assertEqual(controller_response.worker_id, member_id)

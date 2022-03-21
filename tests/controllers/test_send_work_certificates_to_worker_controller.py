from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import SendWorkCertificatesToWorkerRequest
from arbeitszeit_web.controllers.send_work_certificates_to_worker_controller import (
    ControllerRejection,
    SendWorkCertificatesToWorkerController,
)
from tests.flask_integration.request import FakeRequest
from tests.session import FakeSession


class SendCertificatesControllerTests(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.request = FakeRequest()
        self.controller = SendWorkCertificatesToWorkerController(
            session=self.session, request=self.request
        )

    def test_when_company_is_not_authenticated_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", str(uuid4()))
        self.request.set_form("amount", "10")
        self.session.set_current_user_id(None)
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_no_member_id_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", "")
        self.request.set_form("amount", "10")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_malformed_member_id_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", "invalid_id")
        self.request.set_form("amount", "10")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_no_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", str(uuid4()))
        self.request.set_form("amount", "")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_malformed_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", str(uuid4()))
        self.request.set_form("amount", "abc")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.invalid_input,
        )

    def test_when_there_is_negative_amount_then_we_get_the_adequate_controller_rejection(
        self,
    ) -> None:
        self.request.set_form("member_id", str(uuid4()))
        self.request.set_form("amount", "-1")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, ControllerRejection)
        self.assertEqual(
            controller_response.reason,
            ControllerRejection.RejectionReason.negative_amount,
        )

    def test_a_use_case_request_can_get_returned(
        self,
    ) -> None:
        self.request.set_form("member_id", str(uuid4()))
        self.request.set_form("amount", "10")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        self.assertIsInstance(controller_response, SendWorkCertificatesToWorkerRequest)

    def test_a_use_case_request_with_correct_attributes_can_get_returned(
        self,
    ) -> None:
        member_id = uuid4()
        self.request.set_form("member_id", str(member_id))
        self.request.set_form("amount", "10")
        user_id = uuid4()
        self.session.set_current_user_id(user_id)
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, SendWorkCertificatesToWorkerRequest)
        self.assertEqual(controller_response.company_id, user_id)
        self.assertEqual(controller_response.worker_id, member_id)
        self.assertEqual(controller_response.amount, Decimal("10"))

    def test_worker_uuid_gets_stripped(
        self,
    ) -> None:
        member_id = uuid4()
        self.request.set_form("member_id", " " + str(member_id) + " ")
        self.request.set_form("amount", "10")
        self.session.set_current_user_id(uuid4())
        controller_response = self.controller.create_use_case_request()
        assert isinstance(controller_response, SendWorkCertificatesToWorkerRequest)
        self.assertEqual(controller_response.worker_id, member_id)

from arbeitszeit_web.api.controllers.login_member_api_controller import (
    LoginMemberApiController,
    login_member_expected_inputs,
)
from arbeitszeit_web.api.controllers.parameters import BodyParameter
from arbeitszeit_web.api.response_errors import BadRequest
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LoginMemberApiController)

    def test_bad_request_raised_when_request_has_no_email_and_no_password(
        self,
    ) -> None:
        request = FakeRequest()
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(err.exception.message, "Email missing.")

    def test_bad_request_raised_when_request_has_email_but_no_password(self) -> None:
        request = FakeRequest()
        request.set_json({"email": "test@test.org"})
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(err.exception.message, "Password missing.")

    def test_bad_request_raised_when_request_has_password_but_no_email(self) -> None:
        request = FakeRequest()
        request.set_json({"password": "123safe"})
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(err.exception.message, "Email missing.")

    def test_email_and_password_are_passed_to_interactor_request(self) -> None:
        EXPECTED_MAIL = "test@test.org"
        EXPECTED_PASSWORD = "123safe"
        request = FakeRequest()
        request.set_json({"email": EXPECTED_MAIL, "password": EXPECTED_PASSWORD})
        interactor_request = self.controller.create_request(request)
        assert interactor_request
        self.assertEqual(interactor_request.email, EXPECTED_MAIL)
        self.assertEqual(interactor_request.password, EXPECTED_PASSWORD)


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LoginMemberApiController)
        self.inputs = login_member_expected_inputs

    def test_controller_has_two_expected_inputs(self) -> None:
        self.assertEqual(len(self.inputs), 2)

    def test_first_expected_input_is_email(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "email")

    def test_input_email_is_body_param(self) -> None:
        input = self.inputs[0]
        self.assertIsInstance(input, BodyParameter)

    def test_input_email_has_correct_parameters(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "email")
        self.assertEqual(input.type, str)
        self.assertEqual(input.description, "Email.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.required, True)

    def test_second_expected_input_is_password(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "password")

    def test_input_limit_is_body_param(self) -> None:
        input = self.inputs[1]
        self.assertIsInstance(input, BodyParameter)

    def test_input_limit_has_correct_parameters(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "password")
        self.assertEqual(input.type, str)
        self.assertEqual(input.description, "Password.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.required, True)

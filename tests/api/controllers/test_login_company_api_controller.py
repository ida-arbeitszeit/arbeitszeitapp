from arbeitszeit_web.api.controllers.expected_input import InputLocation
from arbeitszeit_web.api.controllers.login_company_api_controller import (
    LoginCompanyApiController,
)
from arbeitszeit_web.api.response_errors import BadRequest
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LoginCompanyApiController)
        self.request = self.injector.get(FakeRequest)

    def test_bad_request_raised_when_request_has_no_email_and_no_password(
        self,
    ) -> None:
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request()
        self.assertEqual(err.exception.message, "Email missing.")

    def test_bad_request_raised_when_request_has_password_but_no_email(self) -> None:
        self.request.set_form(key="password", value="123safe")
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request()
        self.assertEqual(err.exception.message, "Email missing.")

    def test_bad_request_raised_when_request_has_email_but_no_password(self) -> None:
        self.request.set_form(key="email", value="test@test.org")
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request()
        self.assertEqual(err.exception.message, "Password missing.")

    def test_email_and_password_are_passed_to_use_case_request(self) -> None:
        EXPECTED_MAIL = "test@test.org"
        EXPECTED_PASSWORD = "123safe"
        self.request.set_form(key="email", value=EXPECTED_MAIL)
        self.request.set_form(key="password", value=EXPECTED_PASSWORD)
        use_case_request = self.controller.create_request()
        assert use_case_request
        self.assertEqual(use_case_request.email_address, EXPECTED_MAIL)
        self.assertEqual(use_case_request.password, EXPECTED_PASSWORD)


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LoginCompanyApiController)
        self.inputs = self.controller.create_expected_inputs()

    def test_controller_has_two_expected_inputs(self) -> None:
        self.assertEqual(len(self.inputs), 2)

    def test_first_expected_input_is_email(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "email")

    def test_input_email_has_correct_parameters(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "email")
        self.assertEqual(input.type, str)
        self.assertEqual(input.description, "Email.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.location, InputLocation.form)
        self.assertEqual(input.required, True)

    def test_second_expected_input_is_password(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "password")

    def test_input_limit_has_correct_parameters(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "password")
        self.assertEqual(input.type, str)
        self.assertEqual(input.description, "Password.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.location, InputLocation.form)
        self.assertEqual(input.required, True)

from arbeitszeit_web.www.controllers.register_company_controller import (
    RegisterCompanyController,
)
from tests.forms import RegisterFormImpl
from tests.www.base_test_case import BaseTestCase


class RegisterCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterCompanyController)

    def test_that_valid_email_from_form_is_used_in_interactor_request(self) -> None:
        expected_emails = ["test@cp.org", "other@cp.org"]
        for expected_email in expected_emails:
            form = RegisterFormImpl.create(email=expected_email)
            request = self.controller.create_request(form)
            assert request.email == expected_email

    def test_that_name_from_form_is_used_in_interactor_request(self) -> None:
        expected_names = ["testname123", "other name"]
        for expected_name in expected_names:
            form = RegisterFormImpl.create(name=expected_name)
            request = self.controller.create_request(form)
            assert request.name == expected_name

    def test_that_password_from_form_is_use_in_interactor_request(self) -> None:
        expected_passwords = ["admin", "password"]
        for expected_password in expected_passwords:
            form = RegisterFormImpl.create(password=expected_password)
            request = self.controller.create_request(form)
            assert request.password == expected_password

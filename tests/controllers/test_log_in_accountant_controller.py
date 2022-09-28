from unittest import TestCase

from arbeitszeit_web.controllers.log_in_accountant_controller import (
    LogInAccountantController,
)
from tests.forms import LoginForm

from .dependency_injection import get_dependency_injector


class ControllerTester(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.form = LoginForm()
        self.controller = self.injector.get(LogInAccountantController)

    def test_that_email_address_is_taken_from_form(self) -> None:
        expected_email = "test@mail.test"
        form = LoginForm(email_value=expected_email)
        request = self.controller.process_login_form(form)
        self.assertEqual(request.email_address, expected_email)

    def test_that_password_is_taken_from_form(self) -> None:
        expected_password = "test password 123"
        form = LoginForm(password_value=expected_password)
        request = self.controller.process_login_form(form)
        self.assertEqual(request.password, expected_password)

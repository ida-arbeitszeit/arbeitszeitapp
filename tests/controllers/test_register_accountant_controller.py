from typing import Optional
from unittest import TestCase

from arbeitszeit_web.controllers.register_accountant_controller import (
    RegisterAccountantController,
)


class ControllerTests(TestCase):
    def setUp(self) -> None:
        self.controller = RegisterAccountantController()

    def test_that_token_is_correctly_passed_to_request(self) -> None:
        form = FakeForm()
        token = "test token"
        request = self.controller.register_accountant(form, token)
        self.assertEqual(request.token, token)

    def test_that_name_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(name="test name")
        token = "test token"
        request = self.controller.register_accountant(form, token)
        self.assertEqual(request.name, "test name")

    def test_that_password_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(password="test password")
        token = "test token"
        request = self.controller.register_accountant(form, token)
        self.assertEqual(request.password, "test password")

    def test_that_email_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(email="test email")
        token = "test token"
        request = self.controller.register_accountant(form, token)
        self.assertEqual(request.email, "test email")


class FakeForm:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        if name is None:
            name = "test name"
        if password is None:
            password = "test password"
        if email is None:
            email = "test@test.test"
        self.name = name
        self.password = password
        self.email = email

    def get_email_address(self) -> str:
        return self.email

    def get_password(self) -> str:
        return self.password

    def get_name(self) -> str:
        return self.name

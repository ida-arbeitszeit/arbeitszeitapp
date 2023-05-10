from typing import Optional
from unittest import TestCase

from arbeitszeit_web.controllers.register_accountant_controller import (
    RegisterAccountantController,
)
from tests.token import FakeTokenService

from .dependency_injection import get_dependency_injector


class ControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.controller = self.injector.get(RegisterAccountantController)
        self.token_service = self.injector.get(FakeTokenService)

    def test_that_if_token_is_just_some_random_string_then_no_request_is_returned(
        self,
    ) -> None:
        form = FakeForm()
        token = "test token"
        request = self.controller.register_accountant(form, token)
        assert request is None

    def test_that_name_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(name="test name")
        token = self.token_service.generate_token(form.get_email_address())
        request = self.controller.register_accountant(form, token)
        assert request
        self.assertEqual(request.name, "test name")

    def test_that_password_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(password="test password")
        token = self.token_service.generate_token(form.get_email_address())
        request = self.controller.register_accountant(form, token)
        assert request
        self.assertEqual(request.password, "test password")

    def test_that_email_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(email="test email")
        token = self.token_service.generate_token(form.get_email_address())
        request = self.controller.register_accountant(form, token)
        assert request
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

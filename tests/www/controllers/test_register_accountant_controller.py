from typing import Optional

from arbeitszeit_web.www.controllers.register_accountant_controller import (
    RegisterAccountantController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterAccountantController)

    def test_that_name_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(name="test name")
        request = self.controller.create_use_case_request(form)
        assert request
        self.assertEqual(request.name, "test name")

    def test_that_password_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(password="test password")
        request = self.controller.create_use_case_request(form)
        assert request
        self.assertEqual(request.password, "test password")

    def test_that_email_is_correctly_passed_to_request(self) -> None:
        form = FakeForm(email="test email")
        request = self.controller.create_use_case_request(form)
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

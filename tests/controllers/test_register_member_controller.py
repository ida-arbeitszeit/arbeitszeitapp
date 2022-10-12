from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from unittest import TestCase

from arbeitszeit_web.register_member import RegisterMemberController

from .dependency_injection import get_dependency_injector


class RegisterMemberControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.controller = self.injector.get(RegisterMemberController)

    def test_that_strings_are_taken_as_literal_strings_in_request(
        self,
    ) -> None:
        request = self.controller.create_request(
            make_fake_form(email="user@cp.org", name="test_name", password="very_safe"),
        )
        self.assertEqual(request.email, "user@cp.org")
        self.assertEqual(request.name, "test_name")
        self.assertEqual(request.password, "very_safe")


def make_fake_form(
    email: Optional[str] = None,
    name: Optional[str] = None,
    password: Optional[str] = None,
) -> FakeRegisterMemberForm:
    return FakeRegisterMemberForm(
        email=email or "someone@cp.org",
        name=name or "Someone",
        password=password or "super_safe_pw",
    )


@dataclass
class FakeRegisterMemberForm:
    email: str
    name: str
    password: str

    def get_email_string(self) -> str:
        return self.email

    def get_name_string(self) -> str:
        return self.name

    def get_password_string(self) -> str:
        return self.password

    def add_email_error(self, error: str) -> None:
        pass

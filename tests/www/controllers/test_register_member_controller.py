from __future__ import annotations

from typing import Optional
from unittest import TestCase

from arbeitszeit_web.www.controllers.register_member_controller import (
    RegisterMemberController,
)
from tests.forms import RegisterFormImpl

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
) -> RegisterFormImpl:
    return RegisterFormImpl.create(
        email=email or "someone@cp.org",
        name=name or "Someone",
        password=password or "super_safe_pw",
    )

from typing import List
from unittest import TestCase

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(RegisterMemberPresenter)
        self.form = RegisterForm()
        self.translator = self.injector.get(FakeTranslator)

    def test_no_errors_are_rendered_when_registration_was_a_success(self) -> None:
        response = RegisterMemberUseCase.Response(rejection_reason=None)
        self.presenter.present_member_registration(response, self.form)
        self.assertFalse(self.form.errors)

    def test_that_error_message_is_rendered_correctly_when_email_already_exists(
        self,
    ) -> None:
        reason = RegisterMemberUseCase.Response.RejectionReason.member_already_exists
        response = RegisterMemberUseCase.Response(rejection_reason=reason)
        self.presenter.present_member_registration(response, self.form)
        error = self.form.errors[0]
        self.assertEqual(
            error, self.translator.gettext("This email address is already registered.")
        )


class RegisterForm:
    def __init__(self) -> None:
        self.errors: List[str] = []

    def get_email_string(self) -> str:
        return "test@test.test"

    def get_name_string(self) -> str:
        return "test user"

    def get_password_string(self) -> str:
        return "test password"

    def add_email_error(self, error: str) -> None:
        self.errors.append(error)

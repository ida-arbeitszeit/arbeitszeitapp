from typing import List
from unittest import TestCase

from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(RegisterCompanyPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.session = self.injector.get(FakeSession)
        self.form = FakeRegisterForm()

    def test_that_correct_error_message_is_displayed_when_email_is_already_registered(
        self,
    ) -> None:
        reason = RegisterCompany.Response.RejectionReason.company_already_exists
        response = RegisterCompany.Response(rejection_reason=reason)
        self.presenter.present_company_registration(response, self.form)
        self.assertEqual(
            self.form.errors[0],
            self.translator.gettext("This email address is already registered."),
        )

    def test_that_view_model_signals_unsuccessful_view_when_registration_was_rejected(
        self,
    ) -> None:
        reason = RegisterCompany.Response.RejectionReason.company_already_exists
        response = RegisterCompany.Response(rejection_reason=reason)
        view_model = self.presenter.present_company_registration(response, self.form)
        self.assertFalse(view_model.is_success_view)

    def test_that_user_is_not_logged_in_when_registration_was_rejected(
        self,
    ) -> None:
        reason = RegisterCompany.Response.RejectionReason.company_already_exists
        response = RegisterCompany.Response(rejection_reason=reason)
        self.presenter.present_company_registration(response, self.form)
        self.assertFalse(self.session.is_logged_in())

    def test_that_no_error_is_displayed_when_registration_was_successful(self) -> None:
        response = RegisterCompany.Response(rejection_reason=None)
        self.presenter.present_company_registration(response, self.form)
        self.assertFalse(self.form.errors)

    def test_view_model_signals_successful_registration_if_view_model_signals_success(
        self,
    ) -> None:
        response = RegisterCompany.Response(rejection_reason=None)
        view_model = self.presenter.present_company_registration(response, self.form)
        self.assertTrue(view_model.is_success_view)

    def test_that_user_is_logged_in_on_successful_registration(self) -> None:
        response = RegisterCompany.Response(rejection_reason=None)
        self.presenter.present_company_registration(response, self.form)
        self.assertTrue(self.session.is_logged_in())


class FakeRegisterForm:
    def __init__(self) -> None:
        self.errors: List[str] = []

    def get_email_string(self) -> str:
        return "test@test.test"

    def get_name_string(self) -> str:
        return "test name"

    def get_password_string(self) -> str:
        return "test password"

    def add_email_error(self, message: str) -> None:
        self.errors.append(message)

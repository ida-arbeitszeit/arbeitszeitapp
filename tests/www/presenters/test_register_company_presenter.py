from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit_web.www.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from tests.forms import RegisterFormImpl
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

RejectionReason = RegisterCompany.Response.RejectionReason


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterCompanyPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.form = RegisterFormImpl.create()

    def test_that_correct_error_message_is_displayed_when_email_is_already_registered(
        self,
    ) -> None:
        response = self.create_response(
            rejection_reason=RejectionReason.company_already_exists
        )
        self.presenter.present_company_registration(response, self.form)
        self.assertEqual(
            self.form.email_field.errors[0],
            self.translator.gettext("This email address is already registered."),
        )

    def test_that_correct_error_message_is_displayed_on_password_field_when_password_is_invalid(
        self,
    ) -> None:
        response = self.create_response(
            rejection_reason=RejectionReason.user_password_is_invalid
        )
        self.presenter.present_company_registration(response, self.form)
        self.assertEqual(
            self.form.password_field.errors[0],
            self.translator.gettext("Wrong password."),
        )

    def test_that_view_model_signals_unsuccessful_view_when_registration_was_rejected(
        self,
    ) -> None:
        response = self.create_response(
            rejection_reason=RejectionReason.company_already_exists
        )
        view_model = self.presenter.present_company_registration(response, self.form)
        self.assertFalse(view_model.is_success_view)

    def test_that_user_is_not_logged_in_when_registration_was_rejected(
        self,
    ) -> None:
        response = self.create_response(
            rejection_reason=RejectionReason.company_already_exists
        )
        self.presenter.present_company_registration(response, self.form)
        self.assertFalse(self.session.is_logged_in())

    def test_that_no_error_is_displayed_when_registration_was_successful(self) -> None:
        response = self.create_response()
        self.presenter.present_company_registration(response, self.form)
        self.assertFalse(self.form.errors())

    def test_view_model_signals_successful_registration_if_view_model_signals_success(
        self,
    ) -> None:
        response = self.create_response()
        view_model = self.presenter.present_company_registration(response, self.form)
        self.assertTrue(view_model.is_success_view)

    def test_that_user_is_logged_in_on_successful_registration(self) -> None:
        response = self.create_response()
        self.presenter.present_company_registration(response, self.form)
        self.assertTrue(self.session.is_logged_in())

    def create_response(
        self,
        *,
        rejection_reason: Optional[RegisterCompany.Response.RejectionReason] = None,
    ) -> RegisterCompany.Response:
        company_id: Optional[UUID]
        if rejection_reason is None:
            company_id = uuid4()
        else:
            company_id = None
        return RegisterCompany.Response(
            rejection_reason=rejection_reason, company_id=company_id
        )

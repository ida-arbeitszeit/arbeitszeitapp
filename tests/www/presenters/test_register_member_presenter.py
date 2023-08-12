from uuid import uuid4

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.www.presenters.register_member_presenter import (
    RegisterMemberPresenter,
)
from tests.forms import RegisterFormImpl
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

from .url_index import UrlIndexTestImpl


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterMemberPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_no_errors_are_rendered_when_registration_was_a_success(self) -> None:
        form = RegisterFormImpl.create()
        response = self.create_success_response()
        self.presenter.present_member_registration(response, form)
        assert not form.errors()

    def test_that_error_message_is_rendered_correctly_when_email_already_exists(
        self,
    ) -> None:
        form = RegisterFormImpl.create()
        response = self.create_failure_response(
            reason=RegisterMemberUseCase.Response.RejectionReason.member_already_exists
        )
        self.presenter.present_member_registration(response, form)
        error = form.errors()[0]
        self.assertEqual(
            error, self.translator.gettext("This email address is already registered.")
        )

    def test_that_error_message_states_password_mismatch_when_rejection_reason_was_company_with_different_password(
        self,
    ) -> None:
        form = RegisterFormImpl.create()
        response = self.create_failure_response(
            reason=RegisterMemberUseCase.Response.RejectionReason.company_with_different_password_exists
        )
        self.presenter.present_member_registration(response, form)
        error = form.errors()[0]
        self.assertEqual(
            error,
            self.translator.gettext(
                "A company with the same email address already exists but the provided password does not match."
            ),
        )

    def test_that_user_is_not_redirected_on_failure_response(self) -> None:
        form = RegisterFormImpl.create()
        response = self.create_failure_response()
        view_model = self.presenter.present_member_registration(response, form)
        assert view_model.redirect_to is None

    def test_that_user_is_redirected_to_unconfirmed_paged_if_confirmation_is_necessary(
        self,
    ) -> None:
        form = RegisterFormImpl.create()
        response = self.create_success_response(is_confirmation_required=True)
        view_model = self.presenter.present_member_registration(response, form)
        assert view_model.redirect_to == self.url_index.get_unconfirmed_member_url()

    def test_that_user_is_redirected_to_dashboard_if_confirmation_is_not_necessary(
        self,
    ) -> None:
        form = RegisterFormImpl.create()
        response = self.create_success_response(is_confirmation_required=False)
        view_model = self.presenter.present_member_registration(response, form)
        assert view_model.redirect_to == self.url_index.get_member_dashboard_url()

    def create_success_response(
        self, is_confirmation_required: bool = True
    ) -> RegisterMemberUseCase.Response:
        return RegisterMemberUseCase.Response(
            rejection_reason=None,
            user_id=uuid4(),
            is_confirmation_required=is_confirmation_required,
        )

    def create_failure_response(
        self,
        *,
        reason: RegisterMemberUseCase.Response.RejectionReason = RegisterMemberUseCase.Response.RejectionReason.member_already_exists,
    ) -> RegisterMemberUseCase.Response:
        return RegisterMemberUseCase.Response(
            rejection_reason=reason, user_id=None, is_confirmation_required=False
        )

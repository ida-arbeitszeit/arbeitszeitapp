from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from tests.forms import RegisterFormImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(RegisterMemberPresenter)
        self.translator = self.injector.get(FakeTranslator)

    def test_no_errors_are_rendered_when_registration_was_a_success(self) -> None:
        form = RegisterFormImpl.create()
        response = RegisterMemberUseCase.Response(
            rejection_reason=None, user_id=uuid4()
        )
        self.presenter.present_member_registration(response, form)
        assert not form.errors()

    def test_that_error_message_is_rendered_correctly_when_email_already_exists(
        self,
    ) -> None:
        form = RegisterFormImpl.create()
        reason = RegisterMemberUseCase.Response.RejectionReason.member_already_exists
        response = RegisterMemberUseCase.Response(rejection_reason=reason, user_id=None)
        self.presenter.present_member_registration(response, form)
        error = form.errors()[0]
        self.assertEqual(
            error, self.translator.gettext("This email address is already registered.")
        )

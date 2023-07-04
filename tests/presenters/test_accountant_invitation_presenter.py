from datetime import datetime
from typing import Callable
from unittest import TestCase

from arbeitszeit_web.www.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailPresenter,
    ViewModel,
)
from tests.datetime_service import FakeDatetimeService
from tests.email import FakeEmailConfiguration
from tests.token import FakeTokenService
from tests.translator import FakeTranslator

from .accountant_invitation_email_view import AccountantInvitationEmailViewImpl
from .dependency_injection import get_dependency_injector
from .url_index import AccountantInvitationUrlIndexImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.view = self.injector.get(AccountantInvitationEmailViewImpl)
        self.presenter = self.injector.get(AccountantInvitationEmailPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.url_index = self.injector.get(AccountantInvitationUrlIndexImpl)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.token_service = self.injector.get(FakeTokenService)

    def test_that_token_recipient_is_also_mail_recipient(self) -> None:
        expected_recipient = "test@test.test"
        self.presenter.send_accountant_invitation(email=expected_recipient)
        self.assertViewModel(lambda m: expected_recipient in m.recipients)

    def test_that_mail_has_only_one_recipient(self) -> None:
        self.presenter.send_accountant_invitation(email="test@test.test")
        self.assertViewModel(lambda m: len(m.recipients) == 1)

    def test_for_correct_subject_line(self) -> None:
        self.presenter.send_accountant_invitation(email="test@test.test")
        self.assertViewModel(
            lambda m: m.subject
            == self.translator.gettext("Invitation to Arbeitszeitapp")
        )

    def test_that_sender_is_set_to_default_sender(self) -> None:
        self.presenter.send_accountant_invitation(email="test@test.test")
        self.assertViewModel(
            lambda e: e.sender == self.email_configuration.get_sender_address()
        )

    def test_that_invitation_link_is_correct(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        expected_token = self.token_service.generate_token("test@test.test")
        self.presenter.send_accountant_invitation(email="test@test.test")
        self.assertViewModel(
            lambda model: model.registration_link_url
            == self.url_index.get_accountant_invitation_url(expected_token)
        )

    def assertViewModel(self, condition: Callable[[ViewModel], bool]) -> None:
        self.assertTrue(condition(self.view.get_view_model()))

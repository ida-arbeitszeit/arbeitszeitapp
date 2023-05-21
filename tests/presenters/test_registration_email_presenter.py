from datetime import datetime
from unittest import TestCase

from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailPresenter,
)
from tests.datetime_service import FakeDatetimeService
from tests.email import Email, FakeEmailConfiguration, FakeEmailSender
from tests.text_renderer import TextRendererImpl
from tests.token import FakeTokenService
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl


class MemberPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.email_sender = self.injector.get(FakeEmailSender)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_address = "test@test.test"
        self.token_service = self.injector.get(FakeTokenService)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        self.assertTrue(self.email_sender.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_email_is_sent_to_member_address(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        email = self.get_sent_email()
        recipient = email.recipients[0]
        self.assertEqual(self.email_address, recipient)

    def test_that_correct_message_is_rendered(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token(self.email_address)
        expected_url = self.url_index.get_member_confirmation_url(token=token)
        self.presenter.show_member_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(
            email.html,
            self.text_renderer.render_member_registration_message(
                confirmation_url=expected_url
            ),
        )

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))

    def get_sent_email(self) -> Email:
        return self.email_sender.sent_mails[0]


class CompanyPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.email_sender = self.injector.get(FakeEmailSender)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_address = "test@test.test"
        self.token_service = self.injector.get(FakeTokenService)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        self.assertTrue(self.email_sender.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_email_is_sent_to_company_address(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        recipient = email.recipients[0]
        self.assertEqual(self.email_address, recipient)

    def test_that_correct_message_is_rendered(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token(self.email_address)
        expected_url = self.url_index.get_company_confirmation_url(token=token)
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(
            email.html,
            self.text_renderer.render_company_registration_message(
                confirmation_url=expected_url
            ),
        )

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        email = self.get_sent_email()
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))

    def get_sent_email(self) -> Email:
        return self.email_sender.sent_mails[0]

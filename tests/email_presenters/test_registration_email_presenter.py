from datetime import datetime

from arbeitszeit_web.email.registration_email_presenter import (
    RegistrationEmailPresenter,
)
from tests.email import Email, FakeEmailConfiguration
from tests.text_renderer import TextRendererImpl
from tests.token import FakeTokenService
from tests.www.base_test_case import BaseTestCase


class MemberPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_address = "test@test.test"
        self.token_service = self.injector.get(FakeTokenService)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_member_registration_message(self.email_address)
        self.assertTrue(self.email_service.sent_mails)

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
        return self.email_service.sent_mails[0]


class CompanyPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_address = "test@test.test"
        self.token_service = self.injector.get(FakeTokenService)

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_company_registration_message(self.email_address)
        self.assertTrue(self.email_service.sent_mails)

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
        return self.email_service.sent_mails[0]

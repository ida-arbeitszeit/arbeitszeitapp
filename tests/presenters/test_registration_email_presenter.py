from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailPresenter,
)
from tests.email import (
    Email,
    FakeAddressBook,
    FakeEmailConfiguration,
    FakeEmailSender,
    RegistrationEmailTemplateImpl,
)
from tests.text_renderer import TextRendererImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import ConfirmationUrlIndexImpl


class MemberPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_sender = self.injector.get(FakeEmailSender)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.address_book = self.injector.get(FakeAddressBook)
        self.email_template = self.injector.get(RegistrationEmailTemplateImpl)
        self.url_index = self.injector.get(ConfirmationUrlIndexImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.member = uuid4()
        self.token = "some test token"

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_member_registration_message(self.member, self.token)
        self.assertTrue(self.email_sender.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_email_is_sent_to_member_address(self) -> None:
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        recipient = email.recipients[0]
        self.assertEqual(
            self.address_book.get_user_email_address(self.member),
            recipient,
        )

    def test_that_template_is_rendered(self) -> None:
        expected_url = self.url_index.get_confirmation_url(self.token)
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.html, self.email_template.render_to_html(expected_url))

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))

    def get_sent_email(self) -> Email:
        return self.email_sender.sent_mails[0]


class CompanyPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.email_sender = self.injector.get(FakeEmailSender)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.address_book = self.injector.get(FakeAddressBook)
        self.email_template = self.injector.get(RegistrationEmailTemplateImpl)
        self.url_index = self.injector.get(ConfirmationUrlIndexImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegistrationEmailPresenter)
        self.company = uuid4()
        self.token = "some test token"

    def test_that_some_email_is_sent_out(self) -> None:
        self.presenter.show_company_registration_message(self.company, self.token)
        self.assertTrue(self.email_sender.sent_mails)

    def test_that_email_is_sent_to_exactly_one_recipient(self) -> None:
        self.presenter.show_company_registration_message(self.company, self.token)
        email = self.get_sent_email()
        self.assertEqual(len(email.recipients), 1)

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.show_company_registration_message(self.company, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.sender, self.email_configuration.get_sender_address())

    def test_that_email_is_sent_to_company_address(self) -> None:
        self.presenter.show_company_registration_message(self.company, self.token)
        email = self.get_sent_email()
        recipient = email.recipients[0]
        self.assertEqual(
            self.address_book.get_user_email_address(self.company),
            recipient,
        )

    def test_that_template_is_rendered(self) -> None:
        expected_url = self.url_index.get_confirmation_url(self.token)
        self.presenter.show_company_registration_message(self.company, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.html, self.email_template.render_to_html(expected_url))

    def test_that_subject_line_is_correct(self) -> None:
        self.presenter.show_company_registration_message(self.company, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.subject, self.translator.gettext("Account confirmation"))

    def get_sent_email(self) -> Email:
        return self.email_sender.sent_mails[0]

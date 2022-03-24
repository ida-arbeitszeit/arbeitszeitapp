from dataclasses import dataclass
from typing import List
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit_web.presenters.member_registration_email_presenter import (
    MemberRegistrationEmailPresenter,
)
from tests.email import Email, FakeEmailConfiguration, FakeEmailSender


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.email_sender = FakeEmailSender()
        self.email_configuration = FakeEmailConfiguration()
        self.address_book = MemberAddressBook()
        self.email_template = EmailTemplate()
        self.url_index = ConfirmationUrlIndex()
        self.presenter = MemberRegistrationEmailPresenter(
            email_sender=self.email_sender,
            address_book=self.address_book,
            email_template=self.email_template,
            url_index=self.url_index,
            email_configuration=self.email_configuration,
        )
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

    def test_that_temlate_is_rendered(self) -> None:
        expected_url = self.url_index.get_confirmation_url(self.token)
        self.presenter.show_member_registration_message(self.member, self.token)
        email = self.get_sent_email()
        self.assertEqual(email.html, self.email_template.render_to_html(expected_url))

    def get_sent_email(self) -> Email:
        return self.email_sender.sent_mails[0]


class EmailTemplate:
    def render_to_html(self, confirmation_url: str) -> str:
        return f"confirmation mail {confirmation_url}"


class MemberAddressBook:
    def get_user_email_address(self, user: UUID) -> str:
        return f"{user}@test.test"


class ConfirmationUrlIndex:
    def get_confirmation_url(self, token: str) -> str:
        return f"{token} url"

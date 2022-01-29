from unittest import TestCase

from arbeitszeit.token import ConfirmationEmail
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.url_index = ConfirmationUrlIndex()
        self.email_configuration = EmailConfiguration()
        self.presenter = SendConfirmationEmailPresenter(
            url_index=self.url_index, email_configuration=self.email_configuration
        )

    def test_that_confirmation_email_contains_confirmation_url(self) -> None:
        confirmation_token = "test token"
        view_model = self.presenter.render_confirmation_email(
            self.create_confirmation(token=confirmation_token)
        )
        self.assertEqual(
            view_model.confirmation_url,
            self.url_index.get_confirmation_url(confirmation_token),
        )

    def test_that_subject_is_set_correctly(self) -> None:
        view_model = self.presenter.render_confirmation_email(
            self.create_confirmation()
        )
        self.assertEqual(
            view_model.subject,
            "Bitte bestätige dein Konto",
        )

    def test_that_email_address_is_in_recipients(self) -> None:
        expected_email = "test@cp.org"
        view_model = self.presenter.render_confirmation_email(
            self.create_confirmation(email=expected_email)
        )
        self.assertEqual(
            view_model.recipients,
            [expected_email],
        )

    def test_that_sender_address_is_set_correctly(self) -> None:
        view_model = self.presenter.render_confirmation_email(
            self.create_confirmation()
        )
        self.assertEqual(
            view_model.sender,
            self.email_configuration.get_sender_address(),
        )

    def create_confirmation(
        self, token: str = "123", email: str = "testmail@test.org"
    ) -> ConfirmationEmail:
        return ConfirmationEmail(
            token=token,
            email=email,
        )


class ConfirmationUrlIndex:
    def get_confirmation_url(self, token: str) -> str:
        return f"{token} url"


class EmailConfiguration:
    def get_sender_address(self) -> str:
        return "test.sender@email.org"

from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit_web.email.email_change_warning_presenter import (
    EmailChangeWarningPresenter,
)
from tests.email import FakeEmailConfiguration
from tests.text_renderer import TextRendererImpl
from tests.www.base_test_case import BaseTestCase


class EmailChangeWarningPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EmailChangeWarningPresenter)
        self.text_renderer = self.injector.get(TextRendererImpl)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)

    def test_that_one_email_is_sent_when_presenting(self) -> None:
        self.presenter.present_email_change_warning(
            email_change_warning=self.create_email_change_warning(),
        )
        assert len(self.email_service.sent_mails) == 1

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_latest_email_was_sent_to_old_email_address(
        self, expected_email_address: str
    ) -> None:
        self.presenter.present_email_change_warning(
            self.create_email_change_warning(old_email_address=expected_email_address)
        )
        assert self.email_service.sent_mails[-1].recipients == [expected_email_address]

    def test_that_the_content_of_the_mail_is_rendered_correctly(self) -> None:
        old_email = "test@test.test"
        self.presenter.present_email_change_warning(
            self.create_email_change_warning(
                old_email_address=old_email,
            )
        )
        assert self.email_service.sent_mails[
            -1
        ].html == self.text_renderer.render_email_change_warning(
            admin_email_address=self.email_configuration.get_admin_email_address(),
        )

    def test_that_the_subject_line_of_the_sent_mail_is_correct(self) -> None:
        expected_subject = self.translator.gettext("Email address change requested")
        self.presenter.present_email_change_warning(
            self.create_email_change_warning(),
        )
        assert self.email_service.sent_mails[-1].subject == expected_subject

    def test_that_sender_is_the_default_one(self) -> None:
        self.presenter.present_email_change_warning(
            self.create_email_change_warning(),
        )
        assert (
            self.email_service.sent_mails[-1].sender
            == self.email_configuration.get_sender_address()
        )

    def create_email_change_warning(
        self,
        old_email_address: str = "old@test.test",
    ) -> email_notifications.EmailChangeWarning:
        return email_notifications.EmailChangeWarning(
            old_email_address=old_email_address,
        )

from typing import Optional

from arbeitszeit import email_notifications
from arbeitszeit_web.email.cooperation_request_email_presenter import (
    CooperationRequestEmailPresenter,
)
from tests.email import FakeEmailService
from tests.www.base_test_case import BaseTestCase


class CooperationRequestEmailPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CooperationRequestEmailPresenter)
        self.mail_service = self.injector.get(FakeEmailService)

    def test_mail_gets_sent_if_request_was_successful(self) -> None:
        self.presenter.present(self.create_email())
        self.assertTrue(self.mail_service.sent_mails)

    def test_mail_gets_sent_to_coordinator_if_request_was_successful(self) -> None:
        recipient = "company@comp.any"
        self.presenter.present(self.create_email(coordinator_mail=recipient))
        self.assertEqual(self.mail_service.sent_mails[0].recipients, [recipient])

    def test_mail_gets_sent_and_subject_and_html_body_are_not_empty(self) -> None:
        self.presenter.present(self.create_email())
        self.assertTrue(self.mail_service.sent_mails[0].subject)
        self.assertTrue(self.mail_service.sent_mails[0].html)

    def test_mail_html_body_has_name_of_coordinator_safely_escaped(self) -> None:
        coordinator_name = '<a href="dangerous site">coordinator</a>'
        self.presenter.present(self.create_email(coordinator_name=coordinator_name))
        self.assertIn(
            "&lt;a href=&quot;dangerous site&quot;&gt;coordinator&lt;/a&gt;",
            self.mail_service.sent_mails[0].html,
        )

    def create_email(
        self,
        coordinator_mail: Optional[str] = None,
        coordinator_name: Optional[str] = None,
    ) -> email_notifications.CooperationRequestEmail:
        if coordinator_mail is None:
            coordinator_mail = "company@comp.any"
        if coordinator_name is None:
            coordinator_name = "company xy"
        return email_notifications.CooperationRequestEmail(
            coordinator_name=coordinator_name,
            coordinator_email_address=coordinator_mail,
        )

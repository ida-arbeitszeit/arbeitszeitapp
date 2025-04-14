from uuid import uuid4

from arbeitszeit.email_notifications import WorkerRemovalNotification
from arbeitszeit_web.email.notify_about_worker_removal_from_company_presenter import (
    NotifyAboutWorkerRemovalPresenter,
)
from tests.email import FakeEmailConfiguration
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(NotifyAboutWorkerRemovalPresenter)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)

    def test_that_two_emails_get_sent(self) -> None:
        notification_data = WorkerRemovalNotification(
            worker_email="123",
            worker_name="Hans",
            worker_id="4711",
            company_email="456",
            company_name="Wurst",
        )
        self.presenter.notify(message_data=notification_data)
        assert len(self.email_service.sent_mails) == 2

    def test_that_recipients_are_worker_and_company_email(self) -> None:
        expected_recipient_worker = "123"
        expected_recipient_company = "456"
        notification_data = WorkerRemovalNotification(
            worker_email=expected_recipient_worker,
            worker_name="Hans",
            worker_id="4711",
            company_email=expected_recipient_company,
            company_name="Wurst",
        )
        self.presenter.notify(message_data=notification_data)
        assert self.email_service.sent_mails[0].recipients == [
            expected_recipient_worker
        ]
        assert self.email_service.sent_mails[1].recipients == [
            expected_recipient_company
        ]

    def test_that_company_and_worker_names_and_worker_id_appear_in_according_email_bodies(
        self,
    ) -> None:
        expected_company_name = f"{uuid4()}"
        expected_worker_name = f"{uuid4()}"
        expected_worker_id = f"{uuid4()}"
        notification_data = WorkerRemovalNotification(
            worker_email="123",
            worker_name=expected_worker_name,
            worker_id=expected_worker_id,
            company_email="456",
            company_name=expected_company_name,
        )
        self.presenter.notify(message_data=notification_data)
        assert (
            expected_worker_name
            and expected_worker_id in self.email_service.sent_mails[1].html
        )
        assert expected_company_name in self.email_service.sent_mails[0].html

    def test_that_both_emails_have_correct_subject(self) -> None:
        expected_subjects = [
            self.translator.gettext("You have been removed as worker from a company"),
            self.translator.gettext("You have removed a worker from your company"),
        ]
        notification_data = WorkerRemovalNotification(
            worker_email="123",
            worker_name="Hans",
            worker_id="4711",
            company_email="456",
            company_name="Wurst",
        )
        self.presenter.notify(message_data=notification_data)
        assert self.email_service.sent_mails[0].subject == expected_subjects[0]
        assert self.email_service.sent_mails[1].subject == expected_subjects[1]

    def test_that_email_has_correct_sender(self) -> None:
        expected_sender = self.email_configuration.get_sender_address()
        notification_data = WorkerRemovalNotification(
            worker_email="123",
            worker_name="Hans",
            worker_id="4711",
            company_email="456",
            company_name="Wurst",
        )
        self.presenter.notify(message_data=notification_data)
        assert self.email_service.sent_mails[0].sender == expected_sender
        assert self.email_service.sent_mails[1].sender == expected_sender

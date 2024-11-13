from uuid import uuid4

from arbeitszeit_web.email.notify_worker_about_removal_from_company_presenter import (
    NotifyWorkerAboutRemovalPresenter,
)
from tests.email import FakeEmailConfiguration
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(NotifyWorkerAboutRemovalPresenter)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)

    def test_that_one_email_gets_sent(self) -> None:
        self.presenter.notify(worker_email="123", company_name="456")
        assert len(self.email_service.sent_mails) == 1

    def test_that_recipient_is_worker_email(self) -> None:
        expected_recipient = "123"
        self.presenter.notify(worker_email=expected_recipient, company_name="456")
        assert self.email_service.sent_mails[0].recipients == [expected_recipient]

    def test_that_company_name_appers_in_email_body(self) -> None:
        expected_company_name = f"{uuid4()}"
        self.presenter.notify(worker_email="123", company_name=expected_company_name)
        assert expected_company_name in self.email_service.sent_mails[0].html

    def test_that_email_has_correct_subject(self) -> None:
        expected_subject = self.translator.gettext(
            "You have been removed as worker from a company"
        )
        self.presenter.notify(worker_email="123", company_name="456")
        assert self.email_service.sent_mails[0].subject == expected_subject

    def test_that_email_has_correct_sender(self) -> None:
        expected_sender = self.email_configuration.get_sender_address()
        self.presenter.notify(worker_email="123", company_name="456")
        assert self.email_service.sent_mails[0].sender == expected_sender

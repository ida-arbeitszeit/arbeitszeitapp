from html import escape
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit import email_notifications
from arbeitszeit_web.email.request_coordination_transfer_presenter import (
    RequestCoordinationTransferEmailPresenter,
)
from tests.email import FakeEmailConfiguration, FakeEmailService
from tests.www.base_test_case import BaseTestCase


class RequestCoordinationTransferEmailPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCoordinationTransferEmailPresenter)
        self.mail_service = self.injector.get(FakeEmailService)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)

    def test_that_one_mail_is_sent(self) -> None:
        self.presenter.present(self.create_email())
        self.assertEqual(len(self.mail_service.sent_mails), 1)

    def test_mail_gets_sent_and_subject_and_html_body_are_not_empty(self) -> None:
        self.presenter.present(self.create_email())
        self.assertTrue(self.mail_service.sent_mails[0].subject)
        self.assertTrue(self.mail_service.sent_mails[0].html)

    def test_that_subject_is_correct(self) -> None:
        self.presenter.present(self.create_email())
        self.assertEqual(
            self.mail_service.sent_mails[0].subject,
            self.translator.gettext(
                "You are asked to be the coordinator of a cooperation"
            ),
        )

    def test_that_mail_is_sent_to_one_recipient(self) -> None:
        self.presenter.present(self.create_email())
        self.assertEqual(len(self.mail_service.sent_mails[0].recipients), 1)

    def test_that_mail_is_sent_to_the_candidate_specified(self) -> None:
        candidate_mail = "some@mail.com.ar"
        self.presenter.present(self.create_email(candidate_mail=candidate_mail))
        self.assertEqual(self.mail_service.sent_mails[0].recipients[0], candidate_mail)

    def test_that_email_sender_is_set_correctly(self) -> None:
        self.presenter.present(self.create_email())
        self.assertEqual(
            self.mail_service.sent_mails[0].sender,
            self.email_configuration.get_sender_address(),
        )

    def test_that_candidate_name_appears_in_mail_body(self) -> None:
        candidate_name = "some candidate name"
        self.presenter.present(self.create_email(candidate_name=candidate_name))
        self.assertIn(candidate_name, self.mail_service.sent_mails[0].html)

    def test_that_cooperation_name_appears_in_mail_body(self) -> None:
        cooperation_name = "some coop name"
        self.presenter.present(self.create_email(cooperation_name=cooperation_name))
        self.assertIn(cooperation_name, self.mail_service.sent_mails[0].html)

    def test_that_both_candidate_and_cooperation_name_are_safely_escaped_in_html_body(
        self,
    ) -> None:
        dangerous_cooperation_name = '<a href="dangerous site">coop</a>'
        dangerous_candidate_name = '<a href="dangerous site">candidate</a>'
        self.presenter.present(
            self.create_email(
                cooperation_name=dangerous_cooperation_name,
                candidate_name=dangerous_candidate_name,
            )
        )
        self.assertIn(
            escape(dangerous_cooperation_name), self.mail_service.sent_mails[0].html
        )
        self.assertIn(
            escape(dangerous_candidate_name), self.mail_service.sent_mails[0].html
        )

    def test_that_link_to_transfer_request_appears_in_mail_body(self) -> None:
        transfer_request = uuid4()
        expected_link = self.url_index.get_show_coordination_transfer_request_url(
            transfer_request
        )
        self.presenter.present(self.create_email(transfer_request=transfer_request))
        self.assertIn(expected_link, self.mail_service.sent_mails[0].html)

    def create_email(
        self,
        candidate_mail: str = "candidate@comp.any",
        candidate_name: str = "candidate xy",
        cooperation_name: str = "cooperation name",
        transfer_request: Optional[UUID] = None,
    ) -> email_notifications.CoordinationTransferRequest:
        if transfer_request is None:
            transfer_request = uuid4()
        return email_notifications.CoordinationTransferRequest(
            candidate_email=candidate_mail,
            candidate_name=candidate_name,
            cooperation_name=cooperation_name,
            transfer_request=transfer_request,
        )

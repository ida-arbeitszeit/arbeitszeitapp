from arbeitszeit_web.invite_worker_presenter import InviteWorkerPresenterImpl
from tests.email import FakeEmailConfiguration, FakeEmailSender
from tests.presenters.base_test_case import BaseTestCase
from tests.text_renderer import TextRendererImpl
from tests.translator import FakeTranslator


class SendMailTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(InviteWorkerPresenterImpl)
        self.email_service = self.injector.get(FakeEmailSender)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.translator = self.injector.get(FakeTranslator)
        self.text_renderer = self.injector.get(TextRendererImpl)

    def test_one_mail_gets_send(self) -> None:
        self.presenter.show_invite_worker_message(worker_email="member@cp.org")
        self.assertEqual(len(self.email_service.sent_mails), 1)

    def test_mail_gets_send_to_worker_mail(self) -> None:
        expected_mail = "member@cp.org"
        self.presenter.show_invite_worker_message(worker_email=expected_mail)
        self.assertEqual(self.email_service.sent_mails[0].recipients, [expected_mail])

    def test_mail_gets_send_from_configured_mail_sender(self) -> None:
        expected_sender = self.email_configuration.get_sender_address()
        self.presenter.show_invite_worker_message(worker_email="member@cp.org")
        self.assertEqual(self.email_service.sent_mails[0].sender, expected_sender)

    def test_mail_has_correct_subject_line(self) -> None:
        expected_subject = self.translator.gettext(
            "Invitation from a company on Arbeitszeitapp"
        )
        self.presenter.show_invite_worker_message(worker_email="member@cp.org")
        self.assertEqual(self.email_service.sent_mails[0].subject, expected_subject)

    def test_mail_has_correct_html(self) -> None:
        expected_html = (
            self.text_renderer.render_member_notfication_about_work_invitation()
        )
        self.presenter.show_invite_worker_message(worker_email="member@cp.org")
        self.assertEqual(self.email_service.sent_mails[0].html, expected_html)

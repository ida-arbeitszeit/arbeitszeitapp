from arbeitszeit.email_notifications import CooperationRequestEmail
from arbeitszeit_web.email.email_sender import EmailSender
from tests.www.base_test_case import BaseTestCase


class EmailSenderImplTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email_sender_impl = self.injector.get(EmailSender)

    def test(self) -> None:
        email_sent_before = len(self.email_service.sent_mails)
        self.email_sender_impl.send_email(
            CooperationRequestEmail(
                coordinator_email_address="test@test.test",
                coordinator_name="test name",
            )
        )
        assert email_sent_before + 1 == len(self.email_service.sent_mails)

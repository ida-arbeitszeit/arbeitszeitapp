from parameterized import parameterized

from arbeitszeit.email_notifications import (
    CooperationRequestEmail,
    EmailChangeConfirmation,
    Message,
)
from arbeitszeit_web.email.email_sender import EmailSender
from tests.www.base_test_case import BaseTestCase


class EmailSenderImplTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email_sender_impl = self.injector.get(EmailSender)

    @parameterized.expand(
        [
            (
                CooperationRequestEmail(
                    coordinator_email_address="test@test.test",
                    coordinator_name="test name",
                ),
            ),
            (
                EmailChangeConfirmation(
                    old_email_address="test@test.test",
                    new_email_address="test@test.test",
                ),
            ),
        ]
    )
    def test_that_email_is_sent_via_mail_service_with_different_message_types(
        self, message: Message
    ) -> None:
        email_sent_before = len(self.email_service.sent_mails)
        self.email_sender_impl.send_email(message)
        assert email_sent_before + 1 == len(self.email_service.sent_mails)

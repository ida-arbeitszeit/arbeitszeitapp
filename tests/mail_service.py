from typing import List

from injector import singleton

from arbeitszeit.mail_service import MailService


@singleton
class FakeMailService(MailService):
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        pass

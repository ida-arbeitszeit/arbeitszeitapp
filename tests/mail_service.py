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

    def create_confirmation_html(
        self, template_name: str, endpoint: str, token: str
    ) -> str:
        pass

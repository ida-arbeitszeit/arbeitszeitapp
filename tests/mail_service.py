from typing import List

from injector import singleton

from arbeitszeit.mail_service import MailService


@singleton
class FakeMailService(MailService):
    def __init__(self) -> None:
        super().__init__()
        self.sent_mails: List = []

    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        mail = f"Recipients:{recipients},Subject:{subject},Html:{html},Sender:{sender}"
        self.sent_mails.append(mail)

    def create_confirmation_html(
        self, template_name: str, endpoint: str, token: str
    ) -> str:
        return f"Please confirm with your {token} at endpoint {endpoint}"

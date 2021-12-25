from uuid import UUID

from arbeitszeit.use_cases import SendExtMessageRequest


class SendEmailController:
    def __call__(self, message_id: UUID) -> SendExtMessageRequest:
        return SendExtMessageRequest(message_id=message_id)

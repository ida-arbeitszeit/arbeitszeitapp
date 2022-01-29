from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.token import ConfirmationEmail, TokenDeliverer, TokenService


@dataclass
class ResendConfirmationMailResponse:
    class RejectionReason(Exception, Enum):
        sending_mail_failed = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class ResendConfirmationMailRequest:
    subject: str
    recipient: str


@inject
@dataclass
class ResendConfirmationMail:
    token_deliverer: TokenDeliverer
    token_service: TokenService

    def __call__(
        self, request: ResendConfirmationMailRequest
    ) -> ResendConfirmationMailResponse:
        self._create_confirmation_mail(request)
        return ResendConfirmationMailResponse(rejection_reason=None)

    def _create_confirmation_mail(self, request: ResendConfirmationMailRequest) -> None:
        token = self.token_service.generate_token(request.recipient)
        self.token_deliverer.deliver_confirmation_token(
            ConfirmationEmail(
                token=token,
                email=request.recipient,
            )
        )

from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.email import is_possibly_an_email_address
from arbeitszeit.email_notifications import (
    EmailChangeConfirmation,
    EmailChangeWarning,
    EmailSender,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RequestEmailAddressChangeUseCase:
    database: DatabaseGateway
    email_sender: EmailSender

    def request_email_address_change(self, request: Request) -> Response:
        if self._is_valid_request(request):
            self.email_sender.send_email(
                EmailChangeWarning(old_email_address=request.current_email_address)
            )
            self.email_sender.send_email(
                EmailChangeConfirmation(
                    old_email_address=request.current_email_address,
                    new_email_address=request.new_email_address,
                )
            )
            return Response(is_rejected=False)
        return Response(is_rejected=True)

    def _is_valid_request(self, request: Request) -> bool:
        return (
            is_possibly_an_email_address(request.new_email_address)
            and bool(
                self.database.get_email_addresses().with_address(
                    request.current_email_address
                )
            )
            and not self.database.get_email_addresses().with_address(
                request.new_email_address
            )
        )


@dataclass
class Request:
    current_email_address: str
    new_email_address: str


@dataclass
class Response:
    is_rejected: bool

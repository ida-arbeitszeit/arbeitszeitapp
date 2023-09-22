from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.email import is_possibly_an_email_address
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ChangeUserEmailAddressUseCase:
    database: DatabaseGateway

    def change_user_email_address(self, request: Request) -> Response:
        if (
            self.database.get_email_addresses().with_address(request.old_email)
            and not self.database.get_email_addresses().with_address(request.new_email)
            and is_possibly_an_email_address(request.new_email)
        ):
            self.database.create_email_address(
                address=request.new_email, confirmed_on=None
            )
            self.database.get_account_credentials().with_email_address(
                request.old_email
            ).update().change_email_address(request.new_email).perform()
            return Response(is_rejected=False)
        return Response(is_rejected=True)


@dataclass
class Request:
    old_email: str
    new_email: str


@dataclass
class Response:
    is_rejected: bool

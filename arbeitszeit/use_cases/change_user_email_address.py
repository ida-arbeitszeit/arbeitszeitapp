from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.email import is_possibly_an_email_address
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ChangeUserEmailAddressUseCase:
    database: DatabaseGateway

    def change_user_email_address(self, request: Request) -> Response:
        if (
            not self.database.get_email_addresses().with_address(request.new_email)
            and is_possibly_an_email_address(request.new_email)
            and self.database.get_account_credentials().for_user_account_with_id(
                request.user
            )
        ):
            self.database.create_email_address(
                address=request.new_email, confirmed_on=None
            )
            self.database.get_account_credentials().for_user_account_with_id(
                request.user
            ).update().change_email_address(request.new_email).perform()
            return Response(is_rejected=False)
        return Response(is_rejected=True)


@dataclass
class Request:
    user: UUID
    new_email: str


@dataclass
class Response:
    is_rejected: bool

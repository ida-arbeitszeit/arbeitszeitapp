from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email import is_possibly_an_email_address
from arbeitszeit.repositories import AccountCredentialsResult, DatabaseGateway


@dataclass
class ChangeUserEmailAddressInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def change_user_email_address(self, request: Request) -> Response:
        account_credentials = (
            self.database.get_account_credentials().for_user_account_with_id(
                request.user
            )
        )
        if (
            not self.database.get_email_addresses().with_address(request.new_email)
            and is_possibly_an_email_address(request.new_email)
            and account_credentials
        ):
            self.database.create_email_address(
                address=request.new_email, confirmed_on=None
            )
            old_email = self._get_email_before_update(account_credentials)
            account_credentials.update().change_email_address(
                request.new_email
            ).perform()
            self.database.get_email_addresses().with_address(old_email).delete()
            self.database.get_email_addresses().with_address(
                request.new_email
            ).update().set_confirmation_timestamp(self.datetime_service.now()).perform()
            return Response(is_rejected=False)
        return Response(is_rejected=True)

    def _get_email_before_update(
        self, account_credentials: AccountCredentialsResult
    ) -> str:
        first_record = account_credentials.first()
        assert first_record is not None
        return first_record.email_address


@dataclass
class Request:
    user: UUID
    new_email: str


@dataclass
class Response:
    is_rejected: bool

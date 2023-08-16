from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisterAccountantUseCase:
    @dataclass
    class Request:
        email: str
        name: str
        password: str

    @dataclass
    class Response:
        is_accepted: bool
        user_id: Optional[UUID]
        email_address: str

    password_hasher: PasswordHasher
    database: DatabaseGateway
    datetime_service: DatetimeService

    def register_accountant(self, request: Request) -> Response:
        credentials: records.AccountCredentials
        email_address: records.EmailAddress
        accountant: Optional[records.Accountant]
        now = self.datetime_service.now()
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email)
            .joined_with_email_address_and_accountant()
            .first()
        )
        if not record:
            password_hash = self.password_hasher.calculate_password_hash(
                request.password
            )
            self.database.create_email_address(address=request.email, confirmed_on=now)
            credentials = self.database.create_account_credentials(
                request.email, password_hash
            )
        else:
            credentials, email_address, accountant = record
            if accountant:
                return self._failed_registration(request)
            else:
                self.database.get_email_addresses().with_address(
                    request.email
                ).update().set_confirmation_timestamp(
                    self.datetime_service.now()
                ).perform()
        accountant = self.database.create_accountant(
            account_credentials=credentials.id,
            name=request.name,
        )
        assert accountant
        return self.Response(
            is_accepted=True, user_id=accountant.id, email_address=request.email
        )

    def _failed_registration(self, request: Request) -> Response:
        return self.Response(
            is_accepted=False,
            user_id=None,
            email_address=request.email,
        )

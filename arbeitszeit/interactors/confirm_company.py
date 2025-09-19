from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ConfirmCompanyInteractor:
    @dataclass
    class Request:
        email_address: str

    @dataclass
    class Response:
        is_confirmed: bool
        user_id: Optional[UUID]

    database: DatabaseGateway
    datetime_service: DatetimeService

    def confirm_company(self, request: Request) -> Response:
        record = (
            self.database.get_companies()
            .with_email_address(request.email_address)
            .joined_with_email_address()
            .first()
        )
        if not record:
            return self.Response(
                user_id=None,
                is_confirmed=False,
            )
        company, email = record
        if email.confirmed_on is None:
            self.database.get_email_addresses().with_address(
                request.email_address
            ).update().set_confirmation_timestamp(self.datetime_service.now()).perform()
            return self.Response(is_confirmed=True, user_id=company.id)
        else:
            return self.Response(is_confirmed=False, user_id=None)

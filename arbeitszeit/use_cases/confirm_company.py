from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import CompanyRepository
from arbeitszeit.token import InvitationTokenValidator


@inject
@dataclass
class ConfirmCompanyUseCase:
    @dataclass
    class Request:
        token: str

    @dataclass
    class Response:
        is_confirmed: bool
        user_id: Optional[UUID]

    token_validator: InvitationTokenValidator
    company_repository: CompanyRepository
    datetime_service: DatetimeService

    def confirm_company(self, request: Request) -> Response:
        email_address = self.token_validator.unwrap_confirmation_token(request.token)
        if email_address is None:
            return self.Response(is_confirmed=False, user_id=None)
        company = self.company_repository.get_by_email(email_address)
        assert company
        if company.confirmed_on is None:
            self.company_repository.confirm_company(
                company.id, self.datetime_service.now()
            )
            return self.Response(is_confirmed=True, user_id=company.id)
        else:
            return self.Response(is_confirmed=False, user_id=None)

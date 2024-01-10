from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class LogInCompanyUseCase:
    @dataclass
    class Request:
        email_address: str
        password: str

    class RejectionReason(enum.Enum):
        invalid_email_address = enum.auto()
        invalid_password = enum.auto()

    @dataclass
    class Response:
        is_logged_in: bool
        rejection_reason: Optional[LogInCompanyUseCase.RejectionReason]
        email_address: Optional[str]
        user_id: Optional[UUID]

    database: DatabaseGateway
    password_hasher: PasswordHasher

    def log_in_company(self, request: Request) -> Response:
        credentials_query = self.database.get_account_credentials().with_email_address(
            request.email_address.strip()
        )
        record = credentials_query.joined_with_company().first()
        if not record or not record[1]:
            return self.Response(
                rejection_reason=self.RejectionReason.invalid_email_address,
                is_logged_in=False,
                email_address=None,
                user_id=None,
            )
        credentials, company = record
        assert company
        if not self.password_hasher.is_password_matching_hash(
            password=request.password, password_hash=credentials.password_hash
        ):
            return self.Response(
                rejection_reason=self.RejectionReason.invalid_password,
                is_logged_in=False,
                email_address=None,
                user_id=None,
            )
        if self.password_hasher.is_regeneration_needed(credentials.password_hash):
            credentials_query.update().change_password_hash(
                new_password_hash=self.password_hasher.calculate_password_hash(
                    request.password
                )
            ).perform()
        return self.Response(
            rejection_reason=None,
            is_logged_in=True,
            email_address=request.email_address,
            user_id=company.id,
        )

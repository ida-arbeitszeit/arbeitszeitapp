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
        company = (
            self.database.get_companies()
            .with_email_address(request.email_address)
            .first()
        )
        if company is None:
            reason = self.RejectionReason.invalid_email_address
        elif not self.password_hasher.is_password_matching_hash(
            password=request.password, password_hash=company.password_hash
        ):
            reason = self.RejectionReason.invalid_password
        else:
            return self.Response(
                rejection_reason=None,
                is_logged_in=True,
                email_address=request.email_address,
                user_id=company.id,
            )
        return self.Response(
            rejection_reason=reason,
            is_logged_in=False,
            email_address=None,
            user_id=None,
        )

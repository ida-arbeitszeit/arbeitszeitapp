from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class LogInAccountantUseCase:
    @dataclass
    class Request:
        email_address: str
        password: str

    @enum.unique
    class RejectionReason(enum.Enum):
        wrong_password = enum.auto()
        email_is_not_accountant = enum.auto()

    @dataclass
    class Response:
        user_id: Optional[UUID] = None
        rejection_reason: Optional[LogInAccountantUseCase.RejectionReason] = None

    database: DatabaseGateway
    password_hasher: PasswordHasher

    def log_in_accountant(self, request: Request) -> Response:
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email_address.strip())
            .joined_with_accountant()
            .first()
        )
        if record is None or record[1] is None:
            return self.Response(
                rejection_reason=self.RejectionReason.email_is_not_accountant
            )
        else:
            credentials, accountant = record
            assert accountant
            if not self.password_hasher.is_password_matching_hash(
                password=request.password, password_hash=credentials.password_hash
            ):
                return self.Response(
                    rejection_reason=self.RejectionReason.wrong_password
                )
            return self.Response(user_id=accountant.id)

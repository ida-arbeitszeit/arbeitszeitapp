from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class LogInMemberUseCase:
    @enum.unique
    class RejectionReason(enum.Enum):
        unknown_email_address = enum.auto()
        invalid_password = enum.auto()

    @dataclass
    class Request:
        email: str
        password: str

    @dataclass
    class Response:
        is_logged_in: bool
        rejection_reason: Optional[LogInMemberUseCase.RejectionReason]
        email: str
        user_id: Optional[UUID]

    database: DatabaseGateway
    password_hasher: PasswordHasher

    def log_in_member(self, request: Request) -> Response:
        credentials: records.AccountCredentials
        member: Optional[records.Member]
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email.strip())
            .joined_with_member()
            .first()
        )
        if not record or not record[1]:
            return self.Response(
                is_logged_in=False,
                rejection_reason=self.RejectionReason.unknown_email_address,
                email=request.email,
                user_id=None,
            )
        credentials, member = record
        assert member
        if not self.password_hasher.is_password_matching_hash(
            password=request.password, password_hash=credentials.password_hash
        ):
            return self.Response(
                is_logged_in=False,
                rejection_reason=self.RejectionReason.invalid_password,
                email=request.email,
                user_id=None,
            )
        return self.Response(
            is_logged_in=True,
            rejection_reason=None,
            email=request.email,
            user_id=member.id,
        )

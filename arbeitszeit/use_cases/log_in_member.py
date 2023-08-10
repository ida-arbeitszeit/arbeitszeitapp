from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

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
        member = (
            self.database.get_members()
            .with_email_address(request.email.strip())
            .first()
        )
        if not member:
            reason = self.RejectionReason.unknown_email_address
        elif not self.password_hasher.is_password_matching_hash(
            password=request.password, password_hash=member.password_hash
        ):
            reason = self.RejectionReason.invalid_password
        else:
            return self.Response(
                is_logged_in=True,
                rejection_reason=None,
                email=request.email,
                user_id=member.id,
            )
        return self.Response(
            is_logged_in=False,
            rejection_reason=reason,
            email=request.email,
            user_id=None,
        )

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

from arbeitszeit.repositories import MemberRepository


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

    member_repository: MemberRepository

    def log_in_member(self, request: Request) -> Response:
        reason: Optional[LogInMemberUseCase.RejectionReason] = None
        if self.member_repository.validate_credentials(
            email=request.email, password=request.password
        ):
            return self.Response(
                is_logged_in=True, rejection_reason=reason, email=request.email
            )
        if self.member_repository.has_member_with_email(request.email):
            reason = self.RejectionReason.invalid_password
        else:
            reason = self.RejectionReason.unknown_email_address
        return self.Response(
            is_logged_in=False, rejection_reason=reason, email=request.email
        )

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import AccountantRepository


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

    accountant_repository: AccountantRepository

    def log_in_accountant(self, request: Request) -> Response:
        accountants = self.accountant_repository.get_accountants()
        if not accountants.with_email_address(request.email_address):
            return self.Response(
                rejection_reason=self.RejectionReason.email_is_not_accountant
            )
        user_id = self.accountant_repository.validate_credentials(
            email=request.email_address, password=request.password
        )
        if user_id is None:
            return self.Response(rejection_reason=self.RejectionReason.wrong_password)
        return self.Response(user_id=user_id)

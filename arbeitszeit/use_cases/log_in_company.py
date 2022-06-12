from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

from arbeitszeit.repositories import CompanyRepository


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

    company_repository: CompanyRepository

    def log_in_company(self, request: Request) -> Response:
        if self._is_login_success(request):
            return self.Response(
                rejection_reason=None,
                is_logged_in=True,
                email_address=request.email_address,
            )
        else:
            reason = (
                self.RejectionReason.invalid_password
                if self.company_repository.has_company_with_email(request.email_address)
                else self.RejectionReason.invalid_email_address
            )
            return self.Response(
                rejection_reason=reason,
                is_logged_in=False,
                email_address=None,
            )

    def _is_login_success(self, request: LogInCompanyUseCase.Request) -> bool:
        return bool(
            self.company_repository.validate_credentials(
                email_address=request.email_address,
                password=request.password,
            )
        )

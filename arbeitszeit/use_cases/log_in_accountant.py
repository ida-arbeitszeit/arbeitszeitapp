from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import AccountantRepository


@inject
@dataclass
class LogInAccountantUseCase:
    @dataclass
    class Request:
        email_address: str
        password: str

    @dataclass
    class Response:
        user_id: Optional[UUID]

    accountant_repository: AccountantRepository

    def log_in_accountant(self, request: Request) -> Response:
        user_id = self.accountant_repository.validate_credentials(
            email=request.email_address, password=request.password
        )
        return self.Response(user_id=user_id)

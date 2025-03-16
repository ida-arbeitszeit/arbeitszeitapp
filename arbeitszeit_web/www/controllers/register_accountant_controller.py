from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Protocol

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit_web.token import TokenService


class RegisterAccountantForm(Protocol):
    def get_name(self) -> str: ...

    def get_password(self) -> str: ...

    def get_email_address(self) -> str: ...


@dataclass
class RegisterAccountantController:
    token_service: TokenService

    def register_accountant(
        self, form: RegisterAccountantForm, token: str
    ) -> Optional[RegisterAccountantUseCase.Request]:
        return RegisterAccountantUseCase.Request(
            name=form.get_name(),
            email=form.get_email_address(),
            password=form.get_password(),
        )

    def extract_token(self, token: str) -> str | None:
        return self.token_service.confirm_token(token, timedelta(days=1))

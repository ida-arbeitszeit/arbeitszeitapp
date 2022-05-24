from typing import Protocol

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase


class RegisterAccountantForm(Protocol):
    def get_name(self) -> str:
        ...

    def get_password(self) -> str:
        ...

    def get_email_address(self) -> str:
        ...


class RegisterAccountantController:
    def register_accountant(
        self, form: RegisterAccountantForm, token: str
    ) -> RegisterAccountantUseCase.Request:
        return RegisterAccountantUseCase.Request(
            token=token,
            name=form.get_name(),
            email=form.get_email_address(),
            password=form.get_password(),
        )
